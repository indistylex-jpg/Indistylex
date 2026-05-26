"""Seed dummy orders, customers, and reviews for dashboard demo."""
import random
import json
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User, Address
from app.models.product import Product, ProductVariant
from app.models.order import Order, OrderItem, Payment
from app.models.review import Review

app = create_app()

FIRST_NAMES = ['Rahul', 'Priya', 'Aman', 'Neha', 'Vikram', 'Ananya', 'Rohan', 'Sneha',
               'Arjun', 'Kavita', 'Deepak', 'Pooja', 'Karan', 'Ritu', 'Suresh', 'Meera',
               'Nikhil', 'Swati', 'Aditya', 'Divya']
LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Singh', 'Patel', 'Kumar', 'Reddy', 'Joshi',
              'Nair', 'Mehta', 'Chauhan', 'Rao', 'Das', 'Iyer', 'Shah']
CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata',
          'Jaipur', 'Lucknow', 'Ahmedabad']
STATUSES = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'delivered',
            'delivered', 'cancelled']
PAYMENT_METHODS = ['online', 'online', 'online', 'cod']


def seed_dummy_data():
    with app.app_context():
        # Check if dummy data already exists
        if User.query.filter_by(role='customer').count() >= 15:
            print("Dummy data already seeded. Skipping.")
            return

        print("Seeding dummy customers...")
        customers = []
        for i in range(20):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}{i}@example.com"

            if User.query.filter_by(email=email).first():
                continue

            user = User(
                email=email,
                first_name=first,
                last_name=last,
                phone=f"+91{''.join([str(random.randint(0,9)) for _ in range(10)])}",
                role='customer',
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            user.set_password('demo123456')
            db.session.add(user)
            customers.append(user)

        db.session.flush()
        print(f"  + {len(customers)} customers created")

        # Add addresses for customers
        for user in customers:
            addr = Address(
                user_id=user.id,
                full_name=f"{user.first_name} {user.last_name}",
                phone=user.phone or '+919876543210',
                address_line1=f"{random.randint(1,500)}, Block {random.choice('ABCDEFGH')}",
                address_line2=f"Sector {random.randint(1,100)}",
                city=random.choice(CITIES),
                state='Maharashtra',
                postal_code=f"{random.randint(100000, 999999)}",
                is_default=True
            )
            db.session.add(addr)

        db.session.flush()

        # Get all products for order items
        products = Product.query.filter_by(is_active=True).all()
        if not products:
            print("No products found. Run seed_products.py first.")
            return

        print("Seeding dummy orders...")
        order_count = 0
        for i in range(50):
            customer = random.choice(customers)
            days_ago = random.randint(0, 60)
            order_date = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            status = random.choice(STATUSES)
            payment_method = random.choice(PAYMENT_METHODS)

            # Pick 1-4 random products
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))

            subtotal = 0
            order_items = []
            for product in selected_products:
                variant = product.variants[0] if product.variants else None
                qty = random.randint(1, 3)
                price = float(product.price)
                subtotal += price * qty
                order_items.append({
                    'variant_id': variant.id if variant else None,
                    'product_name': product.name,
                    'product_slug': product.slug,
                    'size': variant.size if variant else 'M',
                    'color': variant.color if variant else 'Default',
                    'price': price,
                    'quantity': qty,
                    'image_url': product.images[0].image_url if product.images else None
                })

            tax = round(subtotal * 0.05, 2)
            shipping = 0 if subtotal > 999 else 99
            discount = round(subtotal * random.choice([0, 0, 0, 0.1, 0.15]), 2)
            total = round(subtotal + tax + shipping - discount, 2)

            address_json = json.dumps({
                'full_name': f"{customer.first_name} {customer.last_name}",
                'phone': customer.phone or '+919876543210',
                'address_line1': f"{random.randint(1,500)}, Sector {random.randint(1,50)}",
                'city': random.choice(CITIES),
                'state': 'Maharashtra',
                'pincode': str(random.randint(100000, 999999))
            })

            order = Order(
                user_id=customer.id,
                status=status,
                subtotal=subtotal,
                tax=tax,
                shipping_cost=shipping,
                discount=discount,
                total=total,
                shipping_address=address_json,
                billing_address=address_json,
                payment_method=payment_method,
                created_at=order_date,
                updated_at=order_date
            )

            if status == 'shipped':
                order.shipped_at = order_date + timedelta(days=2)
            elif status == 'delivered':
                order.shipped_at = order_date + timedelta(days=2)
                order.delivered_at = order_date + timedelta(days=5)

            db.session.add(order)
            db.session.flush()

            # Add order items
            for item_data in order_items:
                item = OrderItem(
                    order_id=order.id,
                    variant_id=item_data['variant_id'],
                    product_name=item_data['product_name'],
                    product_slug=item_data['product_slug'],
                    size=item_data['size'],
                    color=item_data['color'],
                    price=item_data['price'],
                    quantity=item_data['quantity'],
                    image_url=item_data['image_url']
                )
                db.session.add(item)

            # Add payment for online orders
            if payment_method == 'online':
                payment = Payment(
                    order_id=order.id,
                    provider='razorpay',
                    razorpay_order_id=f"order_demo_{order.id}",
                    razorpay_payment_id=f"pay_demo_{order.id}",
                    amount=total,
                    currency='INR',
                    status='captured' if status != 'cancelled' else 'failed'
                )
                db.session.add(payment)

            order_count += 1

        db.session.flush()
        print(f"  + {order_count} orders created")

        # Add some reviews
        print("Seeding dummy reviews...")
        review_count = 0
        delivered_orders = Order.query.filter_by(status='delivered').all()
        for order in delivered_orders[:20]:
            for item in order.items.limit(1):
                product = Product.query.filter_by(slug=item.product_slug).first()
                if product and order.user_id:
                    existing = Review.query.filter_by(user_id=order.user_id, product_id=product.id).first()
                    if not existing:
                        review = Review(
                            user_id=order.user_id,
                            product_id=product.id,
                            rating=random.randint(3, 5),
                            title=random.choice(['Great quality!', 'Love it!', 'Perfect fit', 'Very nice', 'Good value']),
                            comment=random.choice([
                                'Amazing quality fabric. My kid loves it!',
                                'Perfect for the price. Would buy again.',
                                'Fits well and looks great. Fast delivery too.',
                                'Good product, nice colors and comfortable.',
                                'Excellent quality, exactly as described.'
                            ]),
                            is_approved=True,
                            created_at=order.delivered_at or order.created_at + timedelta(days=7)
                        )
                        db.session.add(review)
                        review_count += 1

        db.session.commit()
        print(f"  + {review_count} reviews created")
        print("\nDone! Dashboard should now show full data.")


if __name__ == '__main__':
    seed_dummy_data()
