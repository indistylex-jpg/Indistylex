from datetime import datetime
from slugify import slugify
from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-referential relationship for sub-categories
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic')
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = slugify(self.name)

    @property
    def active_products_count(self):
        return self.products.filter_by(is_active=True).count()

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_at_price = db.Column(db.Numeric(10, 2))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand = db.Column(db.String(100))
    gender = db.Column(db.String(20))  # men, women, girls, kids, unisex
    age_group = db.Column(db.String(20))  # 0-2, 2-4, 4-6, 6-8, 8-12, 12-16, adult
    material = db.Column(db.String(200))
    care_instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variants = db.relationship('ProductVariant', backref='product', lazy='dynamic',
                               cascade='all, delete-orphan')
    images = db.relationship('ProductImage', backref='product', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='ProductImage.sort_order')
    reviews = db.relationship('Review', backref='product', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = slugify(self.name)

    @property
    def primary_image(self):
        img = self.images.filter_by(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img.image_url if img else '/static/images/placeholders/product.png'

    @property
    def all_images(self):
        return [img.image_url for img in self.images.order_by(ProductImage.sort_order).all()]

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def in_stock(self):
        return any(v.stock_quantity > 0 and v.is_active for v in self.variants.all())

    @property
    def total_stock(self):
        return sum(v.stock_quantity for v in self.variants.filter_by(is_active=True).all())

    @property
    def average_rating(self):
        approved_reviews = self.reviews.filter_by(is_approved=True).all()
        if not approved_reviews:
            return 0
        return round(sum(r.rating for r in approved_reviews) / len(approved_reviews), 1)

    @property
    def review_count(self):
        return self.reviews.filter_by(is_approved=True).count()

    @property
    def available_sizes(self):
        return sorted(set(
            v.size for v in self.variants.filter_by(is_active=True).all()
            if v.stock_quantity > 0
        ))

    @property
    def available_colors(self):
        return sorted(set(
            v.color for v in self.variants.filter_by(is_active=True).all()
            if v.stock_quantity > 0
        ))

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductVariant(db.Model):
    __tablename__ = 'product_variants'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'size', 'color', name='uq_product_size_color'),
    )

    def __repr__(self):
        return f'<Variant {self.sku} ({self.size}/{self.color})>'


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(300))
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ProductImage {self.image_url}>'
