from flask import Blueprint, request, jsonify
from app.models.product import Product, Category
from app.models.order import Order
from app.extensions import csrf, limiter
from flask_login import current_user

chatbot_bp = Blueprint('chatbot', __name__)

# Knowledge base for the chatbot
STORE_INFO = {
    'name': 'Indistylex',
    'email': 'support@indistylex.in',
    'phone': '+91-6394142176',
    'hours': 'Mon–Sat, 10 AM – 7 PM IST',
    'shipping_time': '3–7 business days',
    'free_shipping_above': 999,
    'return_window': '7 days',
    'currency': '₹',
}

# Intent patterns — keyword lists mapped to response generators
INTENTS = [
    {
        'keywords': ['track', 'tracking', 'where is my order', 'order status', 'my order'],
        'handler': '_handle_order_tracking',
    },
    {
        'keywords': ['return', 'refund', 'exchange', 'replace'],
        'handler': '_handle_returns',
    },
    {
        'keywords': ['shipping', 'delivery', 'deliver', 'ship', 'how long'],
        'handler': '_handle_shipping',
    },
    {
        'keywords': ['size', 'sizing', 'measurement', 'size guide', 'fit'],
        'handler': '_handle_sizing',
    },
    {
        'keywords': ['payment', 'pay', 'upi', 'card', 'razorpay', 'cod', 'cash on delivery'],
        'handler': '_handle_payment',
    },
    {
        'keywords': ['discount', 'coupon', 'offer', 'sale', 'promo', 'code'],
        'handler': '_handle_discounts',
    },
    {
        'keywords': ['contact', 'support', 'help', 'customer care', 'phone', 'email'],
        'handler': '_handle_contact',
    },
    {
        'keywords': ['category', 'categories', 'kids', 'women', 'men', 'girls', 'what do you sell'],
        'handler': '_handle_categories',
    },
    {
        'keywords': ['new arrival', 'new', 'latest', 'trending', 'popular', 'featured'],
        'handler': '_handle_new_arrivals',
    },
    {
        'keywords': ['price', 'cost', 'how much', 'expensive', 'cheap', 'affordable', 'budget'],
        'handler': '_handle_pricing',
    },
    {
        'keywords': ['hi', 'hello', 'hey', 'good morning', 'good evening', 'namaste'],
        'handler': '_handle_greeting',
    },
    {
        'keywords': ['bye', 'goodbye', 'thank', 'thanks', 'thankyou'],
        'handler': '_handle_goodbye',
    },
]


def _handle_greeting(msg):
    return (
        "Hello! 👋 Welcome to Indistylex. How can I help you today?\n\n"
        "I can assist you with:\n"
        "• 📦 Order tracking\n"
        "• 🚚 Shipping info\n"
        "• 📏 Size guide\n"
        "• 💳 Payment methods\n"
        "• 🔄 Returns & refunds\n"
        "• 🏷️ Discounts & offers\n"
        "• 🛍️ Product recommendations"
    )


def _handle_goodbye(msg):
    return (
        "Thank you for shopping with Indistylex! 🙏\n"
        "Have a wonderful day. Feel free to come back anytime!"
    )


def _handle_order_tracking(msg):
    if current_user.is_authenticated:
        latest_order = Order.query.filter_by(
            user_id=current_user.id
        ).order_by(Order.created_at.desc()).first()
        if latest_order:
            return (
                f"📦 Your latest order **#{latest_order.order_number}** is "
                f"**{latest_order.status.replace('_', ' ').title()}**.\n\n"
                "You can view all your orders in the "
                "[My Orders](/orders) section of your account."
            )
        return (
            "You don't have any orders yet. Start shopping our "
            "[latest collection](/shop) today!"
        )
    return (
        "Please [log in](/auth/login) to track your orders.\n"
        "If you checked out as a guest, please contact us at "
        f"{STORE_INFO['email']} with your order number."
    )


def _handle_returns(msg):
    return (
        f"🔄 **Returns & Refunds Policy:**\n\n"
        f"• Return window: **{STORE_INFO['return_window']}** from delivery\n"
        "• Items must be unworn, unwashed, with tags attached\n"
        "• Refunds are processed within 5–7 business days\n"
        "• Exchange available for different size/colour\n\n"
        "To initiate a return, visit [My Orders](/orders) or contact us at "
        f"{STORE_INFO['email']}."
    )


def _handle_shipping(msg):
    return (
        f"🚚 **Shipping Information:**\n\n"
        f"• Standard delivery: **{STORE_INFO['shipping_time']}**\n"
        f"• Free shipping on orders above **{STORE_INFO['currency']}{STORE_INFO['free_shipping_above']}**\n"
        "• We ship across India\n"
        "• You'll receive a tracking link via email once shipped\n\n"
        "Need faster delivery? Check express options at checkout!"
    )


def _handle_sizing(msg):
    return (
        "📏 **Size Guide:**\n\n"
        "We have a detailed size chart for all categories. "
        "Visit our [Size Guide](/size-guide) page for measurements.\n\n"
        "**Quick tips:**\n"
        "• Measure yourself before ordering\n"
        "• When in doubt, go one size up\n"
        "• Check individual product pages for model measurements"
    )


def _handle_payment(msg):
    return (
        "💳 **Payment Methods:**\n\n"
        "We accept:\n"
        "• UPI (Google Pay, PhonePe, Paytm)\n"
        "• Debit & Credit Cards (Visa, Mastercard, Rupay)\n"
        "• Net Banking\n"
        "• Wallets\n\n"
        "All payments are secured by **Razorpay** with 256-bit encryption. "
        "Your card details are never stored on our servers."
    )


def _handle_discounts(msg):
    return (
        "🏷️ **Discounts & Offers:**\n\n"
        "• Check our [Shop](/shop) page for ongoing sales\n"
        "• Apply coupon codes at checkout for extra savings\n"
        "• Sign up for our newsletter for exclusive deals\n"
        "• Follow us on social media for flash sale alerts!\n\n"
        "Have a coupon code? Apply it in your cart before checkout."
    )


def _handle_contact(msg):
    return (
        f"📞 **Contact Us:**\n\n"
        f"• Email: **{STORE_INFO['email']}**\n"
        f"• Phone: **{STORE_INFO['phone']}**\n"
        f"• Business hours: **{STORE_INFO['hours']}**\n\n"
        "You can also visit our [Contact](/contact) page to send us a message. "
        "We typically respond within 24 hours."
    )


def _handle_categories(msg):
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    if categories:
        cat_list = '\n'.join(f"• [{c.name}](/shop?category={c.slug})" for c in categories)
        return f"🛍️ **Our Collections:**\n\n{cat_list}\n\nBrowse our [full shop](/shop) for all products!"
    return "🛍️ Browse our [full shop](/shop) for all products!"


def _handle_new_arrivals(msg):
    products = Product.query.filter_by(is_active=True).order_by(
        Product.created_at.desc()
    ).limit(5).all()
    if products:
        product_list = '\n'.join(
            f"• [{p.name}](/product/{p.slug}) — ₹{p.price}" for p in products
        )
        return f"✨ **New Arrivals:**\n\n{product_list}\n\n[View all →](/shop)"
    return "Check out our [shop](/shop) for the latest arrivals!"


def _handle_pricing(msg):
    return (
        "💰 **Pricing:**\n\n"
        "We offer fashion for every budget!\n"
        "• Browse by price on our [shop page](/shop)\n"
        "• Use the price filter to find items in your range\n"
        f"• Free shipping on orders above ₹{STORE_INFO['free_shipping_above']}\n\n"
        "Look for sale tags for the best deals!"
    )


def _match_intent(message):
    """Match user message to the best intent."""
    msg_lower = message.lower().strip()


    for intent in INTENTS:
        for keyword in intent['keywords']:
            if keyword in msg_lower:
                handler = globals()[intent['handler']]
                return handler(msg_lower)

    # Product search fallback
    products = Product.query.filter(
        Product.is_active == True,
        (Product.name.ilike(f'%{msg_lower}%')) |
        (Product.brand.ilike(f'%{msg_lower}%'))
    ).limit(5).all()

    if products:
        product_list = '\n'.join(
            f"• [{p.name}](/product/{p.slug}) — ₹{p.price}" for p in products
        )
        return f"🔍 I found these products for you:\n\n{product_list}\n\n[Search more →](/shop?q={message})"

    return (
        "I'm not sure I understand that. Here's what I can help with:\n\n"
        "• **Order tracking** — \"Where is my order?\"\n"
        "• **Shipping** — \"How long does delivery take?\"\n"
        "• **Returns** — \"How do I return an item?\"\n"
        "• **Sizing** — \"What size should I get?\"\n"
        "• **Payments** — \"What payment methods do you accept?\"\n"
        "• **Products** — Try typing a product name!\n\n"
        "Or contact our support at " + STORE_INFO['email']
    )


@chatbot_bp.route('/message', methods=['POST'])
@limiter.limit("30 per minute")
def chat_message():
    """Handle chatbot messages."""
    data = request.get_json()
    if not data or not data.get('message', '').strip():
        return jsonify({'reply': 'Please type a message to get started! 😊'}), 200

    user_message = data['message'].strip()
    # Limit message length
    if len(user_message) > 500:
        user_message = user_message[:500]

    reply = _match_intent(user_message)
    return jsonify({'reply': reply})


@chatbot_bp.route('/suggestions', methods=['GET'])
@limiter.limit("20 per minute")
def suggestions():
    """Return quick-reply suggestions."""
    return jsonify({
        'suggestions': [
            'Track my order',
            'Shipping info',
            'Size guide',
            'Payment methods',
            'Returns & refunds',
            'New arrivals',
            'Contact support',
        ]
    })
