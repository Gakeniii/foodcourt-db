from app import app
from models import db, User, Outlet, OwnerMenu, MenuItem, Order, OrderItem, TableBooking
from datetime import datetime, timedelta, timezone
import random

# Sample Data
user_data = [
    {"username": "john_doe", "email": "john@gmail.com", "password": "0000", "role": "customer"},
    {"username": "jane_smith", "email": "jane@gmail.com", "password": "9999", "role": "customer"},
    {"username": "alex_brown", "email": "alex@gmail.com", "password": "8888", "role": "customer"},
    {"username": "lisa_wilson", "email": "lisa@gmail.com", "password": "7777", "role": "customer"},
    {"username": "mark_jones", "email": "mark@gmail.com", "password": "6666", "role": "customer"},
    {"username": "chef_gordon", "email": "gordon@gmail.com", "password": "5555", "role": "owner"},
    {"username": "chef_oliver", "email": "oliver@gmail.com", "password": "4444", "role": "owner"},
    {"username": "james", "email": "james@gmail.com", "password": "3333", "role": "owner"},
    {"username": "susan", "email": "susan@gmail.com", "password": "2222", "role": "owner"},
    {"username": "kevin", "email": "kevin@gmail.com", "password": "1111", "role": "owner"},
]

outlet_data = [
    {"name": "The Food Spot", "image_url": "https://example.com/foodspot.jpg"},
    {"name": "Grill House", "image_url": "https://example.com/grillhouse.jpg"},
    {"name": "Pasta Corner", "image_url": "https://example.com/pastacorner.jpg"},
    {"name": "Sushi Bar", "image_url": "https://example.com/sushibar.jpg"},
    {"name": "Burger Haven", "image_url": "https://example.com/burgerhaven.jpg"},
]

menu_data = [
    {"name": "Cheeseburger", "price": 1200, "image_url": "https://example.com/cheeseburger.jpg", "cuisine": "American", "category": "Fast Food", "waiting": 15},
    {"name": "Pasta Carbonara", "price": 2200, "image_url": "https://example.com/pasta.jpg", "cuisine": "Italian", "category": "Main Course", "waiting": 20},
    {"name": "Sushi Platter", "price": 4500, "image_url": "https://example.com/sushi.jpg", "cuisine": "Japanese", "category": "Main Course", "waiting": 25},
    {"name": "Nyama Choma Ribs", "price": 2200, "image_url": "https://example.com/steak.jpg", "cuisine": "Kenyan", "category": "Main Course", "waiting": 30},
    {"name": "Vegan Salad", "price": 800, "image_url": "https://example.com/salad.jpg", "cuisine": "Vegan", "category": "Salad", "waiting": 10},
]

order_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
payment_methods = ["Apple Pay", "M-Pesa", "Cash", "Card"]

with app.app_context():
    db.drop_all()
    db.create_all()
    
    users = [User(**data) for data in user_data]
    db.session.add_all(users)
    db.session.commit()
    
    owners = User.query.filter_by(role='owner').all()
    customers = User.query.filter_by(role='customer').all()
    
    outlets = [Outlet(name=outlet_data[i]["name"], image_url=outlet_data[i]["image_url"], owner_id=owners[i % len(owners)].id) for i in range(5)]
    db.session.add_all(outlets)
    db.session.commit()
    
    menu_items = []
    for i in range(5):
        outlet = outlets[i % len(outlets)]
        menu_item = MenuItem(
            name=menu_data[i]['name'],
            price=menu_data[i]['price'],
            image_url=menu_data[i]['image_url'],
            cuisine=menu_data[i]['cuisine'],
            category=menu_data[i]['category'],
            waiting=menu_data[i]['waiting'],
            outlet_id=outlet.id
        )
        menu_items.append(menu_item)
    db.session.add_all(menu_items)
    db.session.commit()
    
    orders = []
    for _ in range(7):
        order = Order(
            customer_id=random.choice(customers).id,
            outlet_id=random.choice(outlets).id,
            status=random.choice(order_statuses),
            table_number=random.randint(1, 20)
        )
        orders.append(order)
    db.session.add_all(orders)
    db.session.commit()
    
    order_items = []
    for order in orders:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=random.choice(menu_items).id,
            quantity=random.randint(1, 20),
            payment_method=random.choice(payment_methods)
        )
        order_items.append(order_item)
    db.session.add_all(order_items)
    db.session.commit()
    
    bookings = []
    for _ in range(7):
        booking_time = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 10), hours=random.randint(1, 24))
        booking = TableBooking(
            customer_id=random.choice(customers).id,
            table_number=random.randint(1, 20),
            booking_time=booking_time
        )
        bookings.append(booking)
    db.session.add_all(bookings)
    db.session.commit()
    
    print("Database seeded successfully!")