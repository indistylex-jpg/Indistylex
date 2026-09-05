"""Gemini-powered shopping assistant for Indistylex storefront chatbot."""
from flask import url_for

from app.models.product import Product, Category
from app.services.gemini_service import generate_text, gemini_configured


def chatbot_ai_configured():
    return gemini_configured()


def _store_policies():
    from app.routes.chatbot import get_store_info
    info = get_store_info()
    return f"""
Store: Indistylex — kids fashion online (India).
Email: {info['email']} | Phone: {info['phone']}
Hours: {info['hours']}
Shipping: {info['shipping_time']}, free above {info['currency']}{info['free_shipping_above']}
Returns: {info['return_window']} hassle-free returns (unused, tags on)
Payments: UPI, cards, net banking, wallets via Razorpay; COD available
Website: https://indistylex.com
"""


def _catalog_snippet(limit=12):
    lines = []
    categories = Category.query.filter_by(is_active=True, parent_id=None).order_by(Category.sort_order).limit(8).all()
    if categories:
        lines.append('Categories: ' + ', '.join(
            f"{c.name} (/shop/category/{c.slug})" for c in categories
        ))

    products = Product.query.filter_by(is_active=True).order_by(Product.views_count.desc()).limit(limit).all()
    if products:
        lines.append('Popular products:')
        for p in products:
            lines.append(f"- {p.name} (/product/{p.slug})")
    return '\n'.join(lines)


def _product_context(slug):
    if not slug:
        return ''
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        return ''
    sizes = sorted({v.size for v in product.variants.filter_by(is_active=True).all() if v.is_active and v.stock_quantity > 0 and v.size})
    return f"""
Customer is viewing this product page:
Name: {product.name}
Category: {product.category.name if product.category else 'N/A'}
Gender: {product.gender or 'kids'}
Material: {product.material or 'N/A'}
Short: {product.short_description or ''}
Sizes in stock: {', '.join(sizes) or 'check product page'}
URL: /product/{product.slug}
Do NOT quote prices — prices are shown on the product page only (set by admin).
Help with sizing, styling, fabric care, and whether it fits their child.
"""


def generate_chat_reply(user_message, history=None, product_slug=None):
    """
    Gemini reply for storefront chat. Returns markdown-ish text with [links](/path).
    Falls back to ValueError if AI unavailable.
    """
    if not chatbot_ai_configured():
        raise ValueError('AI not configured')

    from app.routes.chatbot import get_store_info
    info = get_store_info()

    history = history or []
    history_text = ''
    for turn in history[-6:]:
        role = turn.get('role', 'user')
        text = (turn.get('text') or '')[:300]
        if text:
            history_text += f"{role.upper()}: {text}\n"

    system = f"""You are Indistylex Assistant — helpful, concise shopping helper for parents buying kids clothes online in India.

Rules:
- Answer in friendly English (light Hindi ok for warmth: "ji", "bilkul").
- Use **bold** for emphasis. Use markdown links: [text](/path) for internal site links only.
- Never invent products or policies not in context below.
- Never state product prices — tell customers to check the product page for current price.
- For order tracking, tell users to check [My Orders](/orders) or email {info['email']} with order number.
- Keep replies under 120 words unless sizing guide needed.
- Do not mention you are Gemini/Google. You are Indistylex Assistant.
- Suggest relevant products/categories from catalog when helpful.

{_store_policies()}

{_catalog_snippet()}

{_product_context(product_slug)}
"""

    prompt = f"""Recent conversation:
{history_text or '(new conversation)'}

CUSTOMER: {user_message.strip()}

Reply helpfully as Indistylex Assistant:"""

    return generate_text(prompt, system=system, temperature=0.45, timeout=45).strip()
