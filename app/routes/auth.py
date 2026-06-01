from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.forms.auth_forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.services.email_service import send_welcome_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and user.is_locked:
            flash('Account is temporarily locked. Please try again later.', 'danger')
            return render_template('auth/login.html', form=form)

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html', form=form)

            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()

            login_user(user, remember=form.remember_me.data)

            # Merge guest cart with user cart
            _merge_guest_cart(user)

            next_page = request.args.get('next')
            if next_page and not _is_safe_url(next_page):
                next_page = None
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            # Increment failed attempts
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                db.session.commit()

            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            phone=form.phone.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        send_welcome_email(user)
        login_user(user)
        _merge_guest_cart(user)

        flash('Account created successfully! Welcome to Indistylex.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.is_active:
            token = user.generate_reset_token()
            db.session.commit()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user, reset_url)

        # Always show same message to prevent user enumeration
        flash('If an account exists with that email, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


def _merge_guest_cart(user):
    """Merge guest cart into user cart after login/register."""
    from flask import session
    from app.models.cart import Cart, CartItem

    session_id = session.get('session_id')
    if not session_id:
        return

    guest_cart = Cart.query.filter_by(session_id=session_id, user_id=None).first()
    if not guest_cart:
        return

    user_cart = Cart.query.filter_by(user_id=user.id).first()
    if not user_cart:
        guest_cart.user_id = user.id
        guest_cart.session_id = None
        db.session.commit()
        return

    # Merge items
    for guest_item in guest_cart.items.all():
        existing = CartItem.query.filter_by(
            cart_id=user_cart.id, variant_id=guest_item.variant_id
        ).first()
        if existing:
            existing.quantity += guest_item.quantity
        else:
            guest_item.cart_id = user_cart.id
    db.session.delete(guest_cart)
    db.session.commit()


def _is_safe_url(target):
    """Validate redirect URL to prevent open redirects."""
    from urllib.parse import urlparse, urljoin
    from flask import request
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
