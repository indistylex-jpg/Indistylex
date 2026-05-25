from flask import Blueprint, render_template, request, make_response, url_for, flash, redirect
from app.models.product import Product, Category
from app.extensions import cache, limiter
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@cache.cached(timeout=120)
def index():
    """Homepage with featured products, categories, new arrivals, trending."""
    # Get active top-level categories
    categories = Category.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(Category.sort_order).all()

    # New arrivals (latest active products)
    new_arrivals = Product.query.filter_by(is_active=True).join(Category).filter(
        Category.is_active == True
    ).order_by(Product.created_at.desc()).limit(8).all()

    # Featured products
    featured = Product.query.filter_by(is_active=True, is_featured=True).join(Category).filter(
        Category.is_active == True
    ).order_by(Product.created_at.desc()).limit(8).all()

    # Trending products
    trending = Product.query.filter_by(is_active=True, is_trending=True).join(Category).filter(
        Category.is_active == True
    ).order_by(Product.views_count.desc()).limit(8).all()

    return render_template('home/index.html',
                           categories=categories,
                           new_arrivals=new_arrivals,
                           featured=featured,
                           trending=trending)


@main_bp.route('/about')
@cache.cached(timeout=600)
def about():
    return render_template('pages/about.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return render_template('pages/contact.html')

        # Log the contact message (could be emailed or saved to DB later)
        import logging
        logging.getLogger(__name__).info(
            f'Contact form: name={name}, email={email}, subject={subject}'
        )

        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('pages/contact.html')


@main_bp.route('/privacy-policy')
@cache.cached(timeout=600)
def privacy_policy():
    return render_template('pages/privacy.html')


@main_bp.route('/terms')
@cache.cached(timeout=600)
def terms():
    return render_template('pages/terms.html')


@main_bp.route('/size-guide')
@cache.cached(timeout=600)
def size_guide():
    return render_template('pages/size_guide.html')


@main_bp.route('/faq')
@cache.cached(timeout=600)
def faq():
    return render_template('pages/faq.html')


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate dynamic XML sitemap for SEO."""
    pages = []
    now = datetime.utcnow().strftime('%Y-%m-%d')

    # Static pages
    static_routes = [
        ('main.index', 1.0, 'daily'),
        ('shop.listing', 0.9, 'daily'),
        ('main.about', 0.5, 'monthly'),
        ('main.contact', 0.5, 'monthly'),
        ('main.faq', 0.4, 'monthly'),
        ('main.size_guide', 0.4, 'monthly'),
        ('main.privacy_policy', 0.3, 'yearly'),
        ('main.terms', 0.3, 'yearly'),
    ]
    for route, priority, changefreq in static_routes:
        pages.append({
            'loc': url_for(route, _external=True),
            'lastmod': now,
            'changefreq': changefreq,
            'priority': priority,
        })

    # Category pages
    categories = Category.query.filter_by(is_active=True).all()
    for cat in categories:
        pages.append({
            'loc': url_for('shop.listing', category=cat.slug, _external=True),
            'lastmod': now,
            'changefreq': 'weekly',
            'priority': 0.8,
        })

    # Product pages
    products = Product.query.filter_by(is_active=True).all()
    for product in products:
        lastmod = (product.updated_at or product.created_at or datetime.utcnow()).strftime('%Y-%m-%d')
        pages.append({
            'loc': url_for('product.detail', slug=product.slug, _external=True),
            'lastmod': lastmod,
            'changefreq': 'weekly',
            'priority': 0.7,
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'
    xml += '</urlset>'

    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response


@main_bp.route('/robots.txt')
def robots():
    """Serve robots.txt for search engine crawlers."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /auth/\n"
        "Disallow: /account/\n"
        "Disallow: /cart/\n"
        "Disallow: /checkout/\n"
        "Disallow: /orders/\n"
        "\n"
        f"Sitemap: {url_for('main.sitemap', _external=True)}\n"
    )
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response
