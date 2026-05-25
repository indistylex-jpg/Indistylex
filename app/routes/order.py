from flask import Blueprint, render_template, current_app, request
from flask_login import login_required, current_user
from app.models.order import Order
import json

order_bp = Blueprint('order', __name__)


@order_bp.route('/')
@login_required
def order_history():
    """View order history."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ORDERS_PER_PAGE', 10)

    orders = Order.query.filter_by(user_id=current_user.id).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('user/orders.html', orders=orders)


@order_bp.route('/<order_number>')
@login_required
def order_detail(order_number):
    """View order detail."""
    order = Order.query.filter_by(
        order_number=order_number, user_id=current_user.id
    ).first_or_404()

    # Parse shipping address JSON
    shipping_addr = None
    try:
        shipping_addr = json.loads(order.shipping_address)
    except (json.JSONDecodeError, TypeError):
        pass

    return render_template('user/order_detail.html', order=order, shipping_addr=shipping_addr)
