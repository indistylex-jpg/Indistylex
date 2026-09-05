"""Gemini-powered marketing copy for Indistylex — social, SEO, WhatsApp, email."""
import json

from flask import url_for

from app.services.gemini_service import generate_text, gemini_configured, parse_json_response

BRAND_VOICE = """
Indistylex — premium kids fashion India (newborn to teens).
Tone: warm, trustworthy, parent-friendly, stylish but not cheesy.
Use ₹ for prices. Mention quality fabric, easy returns (7 days), free shipping above ₹999.
Hashtags mix brand (#Indistylex #IndistylexKids) + category tags. No false claims.
"""


def marketing_ai_configured():
    return gemini_configured()


def _product_url(product):
    try:
        return url_for('product.detail', slug=product.slug, _external=True)
    except Exception:
        base = 'https://indistylex.com'
        return f'{base}/product/{product.slug}'


def _product_payload(product=None, form_data=None):
    if product:
        ages = ', '.join(product.age_groups_list) if product.age_groups_list else ''
        sizes = ', '.join(sorted({
            v.size for v in product.variants.filter_by(is_active=True).all() if v.size and v.stock_quantity > 0
        }))
        return {
            'name': product.name,
            'category': product.category.name if product.category else '',
            'gender': product.gender or 'kids',
            'price': float(product.price or 0),
            'compare_at_price': float(product.compare_at_price) if product.compare_at_price else None,
            'short_description': product.short_description or '',
            'description': (product.description or '')[:800],
            'material': product.material or '',
            'brand': product.brand or 'Indistylex',
            'ages': ages,
            'sizes_in_stock': sizes,
            'url': _product_url(product),
        }
    form_data = form_data or {}
    return {
        'name': form_data.get('name', ''),
        'category': form_data.get('category', ''),
        'gender': form_data.get('gender', 'kids'),
        'price': form_data.get('price'),
        'compare_at_price': form_data.get('compare_at_price'),
        'short_description': form_data.get('short_description', ''),
        'description': (form_data.get('description') or '')[:800],
        'material': form_data.get('material', ''),
        'brand': form_data.get('brand', 'Indistylex'),
        'ages': form_data.get('ages', ''),
        'sizes_in_stock': form_data.get('sizes', ''),
        'url': form_data.get('url', 'https://indistylex.com'),
    }


def generate_product_marketing_pack(product=None, form_data=None):
    """Instagram, WhatsApp, Facebook, SEO, email — one JSON pack."""
    if not marketing_ai_configured():
        raise ValueError('Add GEMINI_API_KEY to server .env to use Marketing AI.')

    payload = _product_payload(product, form_data)
    if not (payload.get('name') or '').strip():
        raise ValueError('Product name is required to generate marketing copy.')

    prompt = f"""Create marketing copy for this Indistylex kids product.
Return ONLY valid JSON (no markdown) with these keys:
{{
  "instagram_caption": "150-220 words, emojis ok, line breaks, CTA shop link at end",
  "instagram_hashtags": "15-20 hashtags space-separated",
  "whatsapp_broadcast": "short broadcast for WhatsApp Business, under 400 chars, friendly Hindi-English mix ok",
  "facebook_post": "2-3 sentences + CTA for Facebook Page",
  "reel_hook": "one punchy 5-second reel opening line",
  "seo_title": "under 60 chars for Google",
  "seo_description": "150-160 chars meta description",
  "google_shopping_title": "clear title for Google Merchant",
  "email_subject": "newsletter subject line",
  "email_snippet": "2-3 sentence email promo body with CTA",
  "story_text": "text overlay for Instagram Story (3 short lines)"
}}

Product data:
{payload}
"""
    raw = generate_text(prompt, system=BRAND_VOICE, temperature=0.65, json_mode=True)
    try:
        data = parse_json_response(raw)
    except json.JSONDecodeError as exc:
        raise ValueError('AI returned invalid JSON. Try again.') from exc
    data['product_url'] = payload.get('url')
    return data


def generate_weekly_campaign_ideas():
    """Seven campaign ideas for the week — social, WhatsApp, offers."""
    if not marketing_ai_configured():
        raise ValueError('Add GEMINI_API_KEY to server .env to use Marketing AI.')

    prompt = """Return ONLY valid JSON:
{
  "week_theme": "one line theme for the week",
  "ideas": [
    {
      "day": "Monday",
      "channel": "Instagram",
      "title": "short title",
      "action": "what to post/do",
      "caption_draft": "ready-to-post caption under 120 words"
    }
  ]
}
Give 7 ideas (Mon-Sun) mixing Instagram, WhatsApp status, Reels, and website offers.
Focus on kids fashion, festive season, new arrivals, parent trust, COD/UPI, free shipping ₹999+.
Indian audience (Prayagraj + all India online).
"""
    raw = generate_text(prompt, system=BRAND_VOICE, temperature=0.7, json_mode=True)
    try:
        return parse_json_response(raw)
    except json.JSONDecodeError as exc:
        raise ValueError('AI returned invalid JSON. Try again.') from exc


def generate_brand_snippets(content_type='taglines'):
    """Taglines, bios, or ad headlines for branding."""
    if not marketing_ai_configured():
        raise ValueError('Add GEMINI_API_KEY to server .env to use Marketing AI.')

    prompts = {
        'taglines': 'Return JSON: {"items": ["5 brand taglines under 8 words each for Indistylex kids clothing"]}',
        'bios': 'Return JSON: {"instagram_bio": "...", "facebook_about": "...", "whatsapp_status": "..."}',
        'ads': 'Return JSON: {"headlines": ["5 Google/Meta ad headlines"], "descriptions": ["3 ad descriptions under 90 chars"]}',
    }
    prompt = prompts.get(content_type, prompts['taglines'])
    raw = generate_text(prompt, system=BRAND_VOICE, temperature=0.75, json_mode=True)
    try:
        return parse_json_response(raw)
    except json.JSONDecodeError as exc:
        raise ValueError('AI returned invalid JSON. Try again.') from exc
