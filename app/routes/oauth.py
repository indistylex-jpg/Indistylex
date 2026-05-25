from flask import Blueprint, redirect, url_for, flash, session, current_app
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from app.extensions import db
from app.models.user import User

oauth_bp = Blueprint('oauth', __name__)
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth providers with the Flask app."""
    oauth.init_app(app)

    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    oauth.register(
        name='facebook',
        api_base_url='https://graph.facebook.com/',
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        client_kwargs={'scope': 'email public_profile'},
    )


# ── Google OAuth ───────────────────────────────────────────────────

@oauth_bp.route('/google')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    redirect_uri = url_for('oauth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@oauth_bp.route('/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            user_info = oauth.google.userinfo()
    except Exception:
        flash('Google login failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    return _handle_oauth_login(
        provider='google',
        oauth_id=user_info['sub'],
        email=user_info.get('email', ''),
        first_name=user_info.get('given_name', ''),
        last_name=user_info.get('family_name', ''),
    )


# ── Facebook OAuth ─────────────────────────────────────────────────

@oauth_bp.route('/facebook')
def facebook_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    redirect_uri = url_for('oauth.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@oauth_bp.route('/facebook/callback')
def facebook_callback():
    try:
        token = oauth.facebook.authorize_access_token()
        resp = oauth.facebook.get('me?fields=id,email,first_name,last_name')
        user_info = resp.json()
    except Exception:
        flash('Facebook login failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    return _handle_oauth_login(
        provider='facebook',
        oauth_id=user_info['id'],
        email=user_info.get('email', ''),
        first_name=user_info.get('first_name', ''),
        last_name=user_info.get('last_name', ''),
    )


# ── Shared OAuth handler ──────────────────────────────────────────

def _handle_oauth_login(provider, oauth_id, email, first_name, last_name):
    """Find or create user from OAuth data, log them in."""
    if not email:
        flash('Could not retrieve your email. Please log in with email/password.', 'warning')
        return redirect(url_for('auth.login'))

    email = email.lower().strip()

    # Check if this OAuth account is already linked
    user = User.query.filter_by(oauth_provider=provider, oauth_id=oauth_id).first()

    if not user:
        # Check if a user with this email already exists (registered via password)
        user = User.query.filter_by(email=email).first()
        if user:
            # Link OAuth to existing account
            user.oauth_provider = provider
            user.oauth_id = oauth_id
            db.session.commit()
        else:
            # Create new user
            user = User(
                email=email,
                first_name=first_name or 'User',
                last_name=last_name or '',
                oauth_provider=provider,
                oauth_id=oauth_id,
                is_active=True,
            )
            db.session.add(user)
            db.session.commit()

    if not user.is_active:
        flash('Your account has been deactivated.', 'danger')
        return redirect(url_for('auth.login'))

    login_user(user, remember=True)

    # Merge guest cart
    _merge_guest_cart(user)

    flash(f'Welcome, {user.first_name}!', 'success')
    return redirect(url_for('main.index'))


def _merge_guest_cart(user):
    """Merge guest cart into user cart after OAuth login."""
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
