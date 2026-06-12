from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail


def send_email(to, subject, template, **kwargs):
    """Send an email using a template."""
    msg = Message(
        subject=subject,
        recipients=[to] if isinstance(to, str) else to,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
    )
    msg.html = render_template(template, **kwargs)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email to {to}: {e}')
        return False


def send_welcome_email(user):
    """Send welcome email to new user."""
    return send_email(
        to=user.email,
        subject='Welcome to Indistylex!',
        template='emails/welcome.html',
        user=user,
    )


def send_order_confirmation(order, email=None):
    """Send order confirmation email."""
    recipient = email or (order.user.email if order.user else order.guest_email)
    if not recipient:
        return False

    return send_email(
        to=recipient,
        subject=f'Order Confirmed - {order.order_number}',
        template='emails/order_confirmation.html',
        order=order,
    )


def send_order_status_update(order, email=None):
    """Send order status update email."""
    recipient = email or (order.user.email if order.user else order.guest_email)
    if not recipient:
        return False

    return send_email(
        to=recipient,
        subject=f'Order Update - {order.order_number}',
        template='emails/order_status.html',
        order=order,
    )


def send_password_reset_email(user, reset_url):
    """Send password reset email."""
    return send_email(
        to=user.email,
        subject='Reset Your Password - Indistylex',
        template='emails/password_reset.html',
        user=user,
        reset_url=reset_url,
    )
