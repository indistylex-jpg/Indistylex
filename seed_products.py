"""Seed the database with sample categories, products, variants, and images."""
from app import create_app
from app.extensions import db
from app.models.product import Category, Product, ProductVariant, ProductImage

app = create_app()

# Placeholder images (free, no-auth required)
IMG = {
    'newborn': [
        'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600',
        'https://images.unsplash.com/photo-1471286174890-9c112ffca5b4?w=600',
    ],
    'toddler': [
        'https://images.unsplash.com/photo-1471286174890-9c112ffca5b4?w=600',
        'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600',
    ],
    'boys': [
        'https://images.unsplash.com/photo-1471286174890-9c112ffca5b4?w=600',
        'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600',
    ],
    'girls': [
        'https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=600',
        'https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=600',
    ],
}

CATEGORIES = [
    {'name': 'Newborn (0–12M)', 'slug': 'newborn', 'description': 'Soft essentials for your newest family member', 'sort_order': 1},
    {'name': 'Toddler (1–3Y)', 'slug': 'toddler', 'description': 'Comfy and colourful outfits for active toddlers', 'sort_order': 2},
    {'name': 'Boys (3–12Y)', 'slug': 'boys', 'description': 'Cool styles for young boys', 'sort_order': 3},
    {'name': 'Girls (3–12Y)', 'slug': 'girls', 'description': 'Trendy fashion for young girls', 'sort_order': 4},
]

PRODUCTS = [
    # ── Newborn (0–12M) ──
    {'name': 'Romper - Teddy Print', 'category': 'newborn', 'price': 699, 'compare_at': 999,
     'short': 'Soft organic cotton romper with cute teddy print and snap closures.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Organic Cotton', 'featured': True, 'trending': True, 'age_group': '0-2',
     'sizes': ['0-3M', '3-6M', '6-9M', '9-12M'], 'colors': ['White', 'Yellow', 'Mint'], 'stock': 50, 'img_idx': 0},

    {'name': 'Bodysuit Set - Animal Friends', 'category': 'newborn', 'price': 899, 'compare_at': 1299,
     'short': 'Pack of 3 cotton bodysuits with adorable animal prints.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': '100% Cotton', 'featured': True, 'trending': False, 'age_group': '0-2',
     'sizes': ['0-3M', '3-6M', '6-9M', '9-12M'], 'colors': ['Multipack'], 'stock': 60, 'img_idx': 1},

    {'name': 'Footed Pajama - Stars & Moon', 'category': 'newborn', 'price': 599, 'compare_at': 899,
     'short': 'Cozy fleece footed pajama with stars and moon pattern, zip-up closure.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Micro Fleece', 'featured': False, 'trending': True, 'age_group': '0-2',
     'sizes': ['0-3M', '3-6M', '6-9M', '9-12M'], 'colors': ['Blue', 'Pink', 'Grey'], 'stock': 40, 'img_idx': 0},

    {'name': 'Muslin Swaddle Blanket Set', 'category': 'newborn', 'price': 799, 'compare_at': 1199,
     'short': 'Set of 2 breathable muslin swaddle blankets with gentle prints.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Muslin Cotton', 'featured': False, 'trending': False, 'age_group': '0-2',
     'sizes': ['One Size'], 'colors': ['White/Blue', 'White/Pink'], 'stock': 35, 'img_idx': 1},

    # ── Toddler (1–3Y) ──
    {'name': 'Dungaree Set - Dino Explorer', 'category': 'toddler', 'price': 1199, 'compare_at': 1599,
     'short': 'Cotton dungaree with dinosaur patches and matching striped tee.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton', 'featured': True, 'trending': True, 'age_group': '2-4',
     'sizes': ['1-2Y', '2-3Y', '3-4Y'], 'colors': ['Blue', 'Green'], 'stock': 45, 'img_idx': 0},

    {'name': 'Printed Jogger Set - Rainbow', 'category': 'toddler', 'price': 999, 'compare_at': 1399,
     'short': 'Comfy fleece jogger set with rainbow print sweatshirt.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton Fleece', 'featured': False, 'trending': True, 'age_group': '2-4',
     'sizes': ['1-2Y', '2-3Y', '3-4Y'], 'colors': ['Grey/Rainbow', 'Navy/Rainbow'], 'stock': 40, 'img_idx': 1},

    {'name': 'Cotton Frock - Butterfly Garden', 'category': 'toddler', 'price': 849, 'compare_at': 1199,
     'short': 'Lightweight cotton frock with butterfly print and ruffled sleeves.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Cotton', 'featured': True, 'trending': False, 'age_group': '2-4',
     'sizes': ['1-2Y', '2-3Y', '3-4Y'], 'colors': ['Pink', 'Lavender', 'Yellow'], 'stock': 50, 'img_idx': 0},

    {'name': 'Kurta Pajama - Little Prince', 'category': 'toddler', 'price': 1099, 'compare_at': 1499,
     'short': 'Cotton silk kurta pajama set with subtle embroidery for festive occasions.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton Silk', 'featured': False, 'trending': False, 'age_group': '2-4',
     'sizes': ['1-2Y', '2-3Y', '3-4Y'], 'colors': ['Cream', 'Light Blue', 'Peach'], 'stock': 35, 'img_idx': 1},

    # ── Boys (3–12Y) ──
    {'name': 'Boys Kurta Pajama - Festive Gold', 'category': 'boys', 'price': 1299, 'compare_at': 1799,
     'short': 'Festive kurta pajama set with embroidered neckline and matching bottom.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton Silk', 'featured': True, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '5-6Y', '7-8Y', '9-10Y'], 'colors': ['Cream', 'Light Blue', 'Peach'], 'stock': 35, 'img_idx': 0},

    {'name': 'Track Suit - Sporty Stripes', 'category': 'boys', 'price': 999, 'compare_at': 1499,
     'short': 'Comfortable polyester track suit with contrast stripes, zip-up jacket.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Polyester', 'featured': False, 'trending': True, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Navy/Red', 'Black/White', 'Grey/Green'], 'stock': 30, 'img_idx': 1},

    {'name': 'Cargo Shorts - Adventure', 'category': 'boys', 'price': 699, 'compare_at': 999,
     'short': 'Durable cotton cargo shorts with multiple pockets, perfect for play.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton Twill', 'featured': False, 'trending': False, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Khaki', 'Olive', 'Navy'], 'stock': 55, 'img_idx': 0},

    {'name': 'Polo T-Shirt - Campus Cool', 'category': 'boys', 'price': 599, 'compare_at': 899,
     'short': 'Pique cotton polo with contrast collar, great for school and outings.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Pique Cotton', 'featured': True, 'trending': True, 'age_group': '8-12',
     'sizes': ['5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['White', 'Red', 'Navy', 'Green'], 'stock': 70, 'img_idx': 1},

    {'name': 'Denim Jeans - Slim Fit', 'category': 'boys', 'price': 899, 'compare_at': 1299,
     'short': 'Classic slim-fit denim jeans with stretch for all-day comfort.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Stretch Denim', 'featured': False, 'trending': True, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Dark Blue', 'Light Blue', 'Black'], 'stock': 45, 'img_idx': 0},

    {'name': 'Hooded Sweatshirt - Bear Logo', 'category': 'boys', 'price': 799, 'compare_at': 1199,
     'short': 'Warm cotton-blend hoodie with fun bear graphic and kangaroo pocket.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton Blend Fleece', 'featured': True, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Grey', 'Navy', 'Maroon'], 'stock': 40, 'img_idx': 1},

    {'name': 'Formal Shirt - Gentleman', 'category': 'boys', 'price': 749, 'compare_at': 1099,
     'short': 'Crisp cotton formal shirt ideal for school, parties and special events.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton Poplin', 'featured': False, 'trending': False, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['White', 'Sky Blue', 'Pink'], 'stock': 35, 'img_idx': 0},

    {'name': 'Bermuda Shorts - Tropical', 'category': 'boys', 'price': 599, 'compare_at': 899,
     'short': 'Printed bermuda shorts with tropical leaf design and elastic waist.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Cotton', 'featured': False, 'trending': True, 'age_group': '4-6',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y'], 'colors': ['Green', 'Blue', 'Orange'], 'stock': 50, 'img_idx': 1},

    {'name': 'Ethnic Sherwani Set', 'category': 'boys', 'price': 1999, 'compare_at': 2699,
     'short': 'Rich brocade sherwani with churidar and matching dupatta for festive occasions.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': 'Brocade Silk', 'featured': True, 'trending': True, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '5-6Y', '7-8Y', '9-10Y'], 'colors': ['Gold', 'Maroon', 'Royal Blue'], 'stock': 20, 'img_idx': 0},

    {'name': 'Cotton Pyjama Set - Sleepy Bear', 'category': 'boys', 'price': 649, 'compare_at': 949,
     'short': 'Soft cotton nightwear set with cute bear print for the sweetest dreams.', 'gender': 'kids', 'brand': 'Indistylex',
     'material': '100% Cotton', 'featured': False, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Blue', 'Grey', 'White'], 'stock': 60, 'img_idx': 1},

    # ── Girls (3–12Y) ──
    {'name': 'Lehenga Choli - Princess Pink', 'category': 'girls', 'price': 2499, 'compare_at': 3499,
     'short': 'Glittery net lehenga with sequin work, perfect for weddings and parties.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Net with Satin Lining', 'featured': True, 'trending': True, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '6-7Y', '8-9Y', '10-11Y'], 'colors': ['Pink', 'Lavender', 'Peach'], 'stock': 30, 'img_idx': 0},

    {'name': 'Printed Frock - Summer Bloom', 'category': 'girls', 'price': 899, 'compare_at': 1299,
     'short': 'Colorful cotton frock with floral print and ruffled hem.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Cotton', 'featured': False, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '6-7Y', '8-9Y'], 'colors': ['Yellow', 'Blue', 'Coral'], 'stock': 40, 'img_idx': 1},

    {'name': 'Denim Dungaree Set', 'category': 'girls', 'price': 1499, 'compare_at': 1999,
     'short': 'Soft denim dungaree with striped inner tee, casual and trendy.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Denim + Cotton', 'featured': False, 'trending': True, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y'], 'colors': ['Light Blue', 'Dark Blue'], 'stock': 25, 'img_idx': 0},

    {'name': 'Tutu Skirt - Fairy Sparkle', 'category': 'girls', 'price': 799, 'compare_at': 1199,
     'short': 'Glittery tulle tutu skirt with elastic waistband, dance-ready.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Tulle + Cotton Lining', 'featured': True, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '6-7Y', '8-9Y'], 'colors': ['Pink', 'Gold', 'White'], 'stock': 45, 'img_idx': 1},

    {'name': 'Anarkali Suit - Royal Blossom', 'category': 'girls', 'price': 1799, 'compare_at': 2499,
     'short': 'Elegant flared anarkali suit with embroidery work for festive celebrations.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Chanderi Cotton', 'featured': True, 'trending': True, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '6-7Y', '8-9Y', '10-11Y'], 'colors': ['Rani Pink', 'Teal', 'Mustard'], 'stock': 25, 'img_idx': 0},

    {'name': 'Salwar Kameez - Floral Dream', 'category': 'girls', 'price': 1299, 'compare_at': 1799,
     'short': 'Printed cotton salwar kameez with dupatta, perfect for everyday ethnic wear.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Cotton', 'featured': False, 'trending': False, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Pink', 'Blue', 'Green'], 'stock': 35, 'img_idx': 1},

    {'name': 'Party Gown - Cinderella', 'category': 'girls', 'price': 1999, 'compare_at': 2999,
     'short': 'Layered net party gown with sequin bodice and satin bow detail.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Net + Satin', 'featured': True, 'trending': True, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '6-7Y', '8-9Y', '10-11Y'], 'colors': ['Sky Blue', 'Blush Pink', 'White'], 'stock': 20, 'img_idx': 0},

    {'name': 'Palazzo Set - Sunshine', 'category': 'girls', 'price': 999, 'compare_at': 1399,
     'short': 'Trendy crop top and palazzo pants set with bright floral print.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Rayon', 'featured': False, 'trending': True, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Yellow', 'Pink', 'Aqua'], 'stock': 40, 'img_idx': 1},

    {'name': 'Pattu Pavadai - Temple Gold', 'category': 'girls', 'price': 2199, 'compare_at': 2999,
     'short': 'Traditional South Indian pattu pavadai with zari border for puja and festivals.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Art Silk', 'featured': True, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '4-5Y', '6-7Y', '8-9Y', '10-11Y'], 'colors': ['Red/Gold', 'Green/Gold', 'Purple/Gold'], 'stock': 15, 'img_idx': 0},

    {'name': 'Cotton Nightgown - Sweet Dreams', 'category': 'girls', 'price': 599, 'compare_at': 899,
     'short': 'Soft cotton nightgown with unicorn print and ruffled sleeves.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': '100% Cotton', 'featured': False, 'trending': False, 'age_group': '4-6',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Lilac', 'Pink', 'White'], 'stock': 50, 'img_idx': 1},

    {'name': 'Jogger Set - Active Girl', 'category': 'girls', 'price': 899, 'compare_at': 1299,
     'short': 'Comfy cotton jogger set with graphic sweatshirt for sporty kids.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Cotton Fleece', 'featured': False, 'trending': True, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Grey/Pink', 'Navy/Coral', 'Black/White'], 'stock': 35, 'img_idx': 0},

    {'name': 'Sharara Set - Festive Star', 'category': 'girls', 'price': 1599, 'compare_at': 2199,
     'short': 'Embroidered kurta with flared sharara and matching dupatta for celebrations.', 'gender': 'girls', 'brand': 'Indistylex',
     'material': 'Georgette', 'featured': True, 'trending': False, 'age_group': '6-8',
     'sizes': ['3-4Y', '5-6Y', '7-8Y', '9-10Y', '11-12Y'], 'colors': ['Peach', 'Mint', 'Magenta'], 'stock': 25, 'img_idx': 1},
]


def seed():
    with app.app_context():
        # Create tables if not exist
        db.create_all()

        # Skip if products already exist
        if Product.query.first():
            print('Products already seeded. Skipping.')
            return

        # Create categories
        cat_map = {}
        for c in CATEGORIES:
            cat = Category(
                name=c['name'], slug=c['slug'],
                description=c['description'], sort_order=c['sort_order'],
                is_active=True
            )
            db.session.add(cat)
            db.session.flush()
            cat_map[c['slug']] = cat
            print(f'  + Category: {cat.name}')

        # Create products with variants and images
        sku_counter = 1000
        for p in PRODUCTS:
            cat = cat_map[p['category']]
            product = Product(
                name=p['name'],
                short_description=p['short'],
                description=f"{p['short']} Crafted with premium {p['material'].lower()} for comfort and style. "
                            f"Brand: {p['brand']}. Care: Dry clean or gentle wash as per fabric.",
                price=p['price'],
                compare_at_price=p['compare_at'],
                category_id=cat.id,
                brand=p['brand'],
                gender=p['gender'],
                age_group=p.get('age_group'),
                material=p['material'],
                is_active=True,
                is_featured=p['featured'],
                is_trending=p['trending'],
            )
            db.session.add(product)
            db.session.flush()

            # Add image
            img_url = IMG[p['category']][p['img_idx'] % len(IMG[p['category']])]
            db.session.add(ProductImage(
                product_id=product.id,
                image_url=img_url,
                alt_text=product.name,
                is_primary=True,
                sort_order=0
            ))

            # Add variants (size x color)
            for size in p['sizes']:
                for color in p['colors']:
                    sku_counter += 1
                    db.session.add(ProductVariant(
                        product_id=product.id,
                        size=size,
                        color=color,
                        sku=f'SKW-{sku_counter}',
                        stock_quantity=p['stock'],
                        is_active=True
                    ))

            print(f'  + Product: {product.name}  ({len(p["sizes"])}×{len(p["colors"])} variants)')

        db.session.commit()
        total = Product.query.count()
        variants = ProductVariant.query.count()
        print(f'\nDone! {total} products, {variants} variants seeded.')


if __name__ == '__main__':
    seed()
