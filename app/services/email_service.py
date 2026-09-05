from flask import current_app, render_template, url_for
from flask_mail import Message
from app.extensions import mail


def mail_configured():
    """True when SMTP credentials are set (Gmail app password, etc.)."""
    return bool(
        current_app.config.get('MAIL_USERNAME')
        and current_app.config.get('MAIL_PASSWORD')
    )


def _support_email():
    return current_app.config.get('SUPPORT_EMAIL', 'indistylex@gmail.com')


def _mail_sender():
    sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    if sender:
        return sender
    username = current_app.config.get('MAIL_USERNAME')
    if username:
        return ('Indistylex', username)
    return ('Indistylex', _support_email())


def send_email(to, subject, template, reply_to=None, **kwargs):
    """Send an email using a template."""
    if not mail_configured():
        current_app.logger.warning('Email not sent (MAIL_USERNAME/MAIL_PASSWORD not set): %s', subject)
        return False

    kwargs.setdefault('support_email', _support_email())
    msg = Message(
        subject=subject,
        recipients=[to] if isinstance(to, str) else to,
        sender=_mail_sender(),
        reply_to=reply_to,
    )
    msg.html = render_template(template, **kwargs)
    try:
        mail.send(msg)
        return True
    except Exception as exc:
        current_app.logger.error('Failed to send email to %s: %s', to, exc)
        return False


def send_welcome_email(user):
    """Send welcome email to new user."""
    return send_email(
        to=user.email,
        subject='Welcome to Indistylex!',
        template='emails/welcome.html',
        user=user,
        shop_url=url_for('shop.listing', _external=True),
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


def send_contact_form_email(name, email, subject, message):
    """Notify support inbox when someone submits the contact form."""
    topic = subject or 'Website contact form'
    return send_email(
        to=_support_email(),
        subject=f'[Indistylex Contact] {topic}',
        template='emails/contact_form.html',
        reply_to=email,
        name=name,
        email=email,
        subject_line=topic,
        message=message,
    )
