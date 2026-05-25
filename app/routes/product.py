from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.extensions import db, limiter
from app.models.product import Product, Category
from app.models.review import Review
from app.models.wishlist import Wishlist

product_bp = Blueprint('product', __name__)


@product_bp.route('/<slug>')
def detail(slug):
    """Product detail page."""
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Ensure category is active
    if not product.category.is_active:
        from flask import abort
        abort(404)

    # Increment view count
    product.views_count = (product.views_count or 0) + 1
    db.session.commit()

    # Get approved reviews
    reviews = product.reviews.filter_by(is_approved=True).order_by(
        Review.created_at.desc()
    ).all()

    # Check if current user has wishlisted
    is_wishlisted = False
    if current_user.is_authenticated:
        is_wishlisted = Wishlist.query.filter_by(
            user_id=current_user.id, product_id=product.id
        ).first() is not None

    # Related products (same category)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True,
    ).limit(4).all()

    return render_template('shop/detail.html',
                           product=product,
                           reviews=reviews,
                           is_wishlisted=is_wishlisted,
                           related=related)


@product_bp.route('/<int:product_id>/review', methods=['POST'])
@limiter.limit("5 per minute")
def add_review(product_id):
    """Add a review to a product."""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login required'}), 401

    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    # Check if user already reviewed
    existing = Review.query.filter_by(
        product_id=product_id, user_id=current_user.id
    ).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this product.'}), 400

    rating = data.get('rating')
    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5.'}), 400

    # Sanitize and limit input length
    from markupsafe import escape
    title = str(escape(str(data.get('title', '')).strip()))[:200]
    comment = str(escape(str(data.get('comment', '')).strip()))[:2000]

    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=int(rating),
        title=title,
        comment=comment,
        is_approved=False,  # Requires admin approval
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'message': 'Review submitted and awaiting approval.'}), 201
