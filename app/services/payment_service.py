import razorpay
from flask import current_app
from app.extensions import db
from app.models.order import Payment


def get_razorpay_client():
    """Get configured Razorpay client."""
    return razorpay.Client(
        auth=(
            current_app.config['RAZORPAY_KEY_ID'],
            current_app.config['RAZORPAY_KEY_SECRET'],
        )
    )


def create_razorpay_order(order):
    """Create a Razorpay order for payment."""
    client = get_razorpay_client()

    amount_paise = int(order.total * 100)  # Razorpay expects amount in paise

    razorpay_order = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'receipt': order.order_number,
        'notes': {
            'order_id': order.id,
            'order_number': order.order_number,
        }
    })

    # Create payment record
    payment = Payment(
        order_id=order.id,
        razorpay_order_id=razorpay_order['id'],
        amount=order.total,
        currency='INR',
        status='pending',
    )
    db.session.add(payment)
    db.session.commit()

    return razorpay_order


def verify_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature):
    """Verify Razorpay payment signature."""
    client = get_razorpay_client()

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False


def capture_payment(payment):
    """Update payment record after successful verification."""
    payment.status = 'captured'
    db.session.commit()
    return payment


def process_refund(payment, amount=None):
    """Process refund via Razorpay."""
    client = get_razorpay_client()

    refund_amount = int((amount or payment.amount) * 100)

    refund = client.payment.refund(payment.razorpay_payment_id, {
        'amount': refund_amount,
    })

    payment.status = 'refunded'
    db.session.commit()

    return refund
