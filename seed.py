from app import app
from models import db, User, Outlet, OwnerMenu, MenuItem, Order, OrderItem, TableBooking
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.postgresql import insert
import random


booking_time = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 10), hours=random.randint(1, 24))

categories = ['Starter', 'Main Course', 'Dessert', 'Kids Menu', 'Snacks', 'Drinks']
cuisines = ['Italian', 'Chinese', 'Indian', 'Mexican']

user_data = [
    {"name": "john_doe", "email": "john@gmail.com", "password": generate_password_hash("0000"), "role": "Customer"},
    {"name": "jane_smith", "email": "jane@gmail.com", "password": generate_password_hash("9999"), "role": "Customer"},
    {"name": "alex_brown", "email": "alex@gmail.com", "password": generate_password_hash("8888"), "role": "Customer"},
    {"name": "lisa_wilson", "email": "lisa@gmail.com", "password": generate_password_hash("7777"), "role": "Customer"},
    {"name": "mark_jones", "email": "mark@gmail.com", "password": generate_password_hash("6666"), "role": "Customer"},
    {"name": "chef_gordon", "email": "gordon@gmail.com", "password": generate_password_hash("5555"), "role": "Owner"},
    {"name": "chef_oliver", "email": "oliver@gmail.com", "password": generate_password_hash("4444"), "role": "Owner"},
    {"name": "james", "email": "james@gmail.com", "password": generate_password_hash("3333"), "role": "Owner"},
    {"name": "susan", "email": "susan@gmail.com", "password": generate_password_hash("2222"), "role": "Owner"},
    {"name": "kevin", "email": "kevin@gmail.com", "password": generate_password_hash("1111"), "role": "Owner"},
]

outlet_data = [
    {"name": "Pizza Delights", "image_url": "https://images.pexels.com/photos/17588091/pexels-photo-17588091/free-photo-of-pasta-and-cake-on-table.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Kai Sushi Place", "image_url": "https://images.pexels.com/photos/3147493/pexels-photo-3147493.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Green Garden Salad", "image_url": "https://images.pexels.com/photos/30350305/pexels-photo-30350305/free-photo-of-colorful-fresh-garden-salad-in-white-bowl.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Steak House Supreme", "image_url": "https://images.pexels.com/photos/236887/pexels-photo-236887.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Big Meat O Max", "image_url": "https://images.pexels.com/photos/11089587/pexels-photo-11089587.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Impresso Patisserrie", "image_url": "https://images.pexels.com/photos/16220859/pexels-photo-16220859/free-photo-of-delicious-cupcakes-and-chocolates.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Taco Fiesta", "image_url": "https://images.pexels.com/photos/7388095/pexels-photo-7388095.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Burger Place", "image_url": "https://images.pexels.com/photos/27600009/pexels-photo-27600009/free-photo-of-cheesy-burger.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Vegan Options", "image_url": "https://images.pexels.com/photos/5794779/pexels-photo-5794779.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "SeaFood Sensations", "image_url": "https://images.pexels.com/photos/842142/pexels-photo-842142.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "HomeBoy Cafe", "image_url": "https://images.pexels.com/photos/28895989/pexels-photo-28895989/free-photo-of-delicious-cheesecake-with-lotus-biscuit-topping.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Iglesias Eats", "image_url": "https://images.pexels.com/photos/5229768/pexels-photo-5229768.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
    {"name": "Chun Li's Chinese Delicacies", "image_url": "https://images.pexels.com/photos/3026808/pexels-photo-3026808.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"},
]

menu_data = [
    {"name": "Margharita Pizza", "price": 1200, "image_url": "https://images.pexels.com/photos/30737921/pexels-photo-30737921/free-photo-of-top-view-of-delicious-cheese-pizza-on-wooden-board.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Italian", "category": "Main Course","description": "Classic Margherita pizza with fresh tomatoes, mozzarella, and basil.", "waiting": 15},
    {"name": "Sushi Platter", "price": 2200, "image_url": "https://images.pexels.com/photos/3763816/pexels-photo-3763816.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Japanese", "category": "Main Course","description": "Assorted sushi platter with fresh salmon, tuna, and avocado rolls.", "waiting": 20},
    {"name": "Green Garden Salad", "price": 900, "image_url": "https://images.pexels.com/photos/257816/pexels-photo-257816.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "American", "category": "Appetizer", "description": "Crisp romaine lettuce with Caesar dressing, croutons, and parmesan cheese.", "waiting": 25},
    {"name": "Nyama Choma Ribs", "price": 2200, "image_url": "https://images.pexels.com/photos/15264027/pexels-photo-15264027/free-photo-of-roasted-meat-and-potatoes.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Kenyan", "category": "Main Course", "description": "Grilled Ribs over hot coal for longs periods of time paired with garlic-herb butter.","waiting": 30},
    {"name": "Steak Frites", "price": 800, "image_url": "https://images.pexels.com/photos/10749578/pexels-photo-10749578.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "French", "category": "Main Course", "description": "Grilled steak with a side of crispy French fries and herb butter.", "waiting":25},
    {"name": "Chocolate  Cake", "price": 750, "image_url": "https://images.pexels.com/photos/7381533/pexels-photo-7381533.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "American", "category": "Dessert", "description": "Warm chocolate cake with a gooey center, served with vanilla ice cream.", "waiting":10},
    {"name": "Taco Fiesta", "price": 1100, "image_url": "https://images.pexels.com/photos/8230019/pexels-photo-8230019.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Mexican", "category": "Main Course", "description": "Tacos filled with seasoned beef, lettuce, cheese, and salsa.","waiting":15},
    {"name": "Drip Burger", "price": 1400, "image_url": "https://img.freepik.com/free-photo/front-view-burgers-stand_141793-15545.jpg?t=st=1740133341~exp=1740136941~hmac=72dcf02adc153d8d9752d9d06622ca4b5bb8c183ca15ae6949860eeb570b01ef&w=1800", "cuisine": "American", "category": "Main Course", "description": "Juicy beef burger with extra cheese drip, lettuce, tomato, cheese, and a special sauce.", "waiting":10},
    {"name": "Caesars Salads", "price": 800, "image_url": "https://images.pexels.com/photos/6671871/pexels-photo-6671871.png?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "American", "category": "Appetizer", "description": "Fresh mixed greens with tomatoes, cucumbers, and a light vinaigrette.", "waiting":20},
    {"name": "Seaside Sensations", "price": 3500, "image_url": "https://images.pexels.com/photos/7364105/pexels-photo-7364105.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Sea Food", "category": "Main Course", "description": "A platter of grilled shrimp, scallops, and fish with a lemon butter sauce.", "waiting":20},
    {"name": "Classic NewYork Cheesecakes", "price": 800, "image_url": "https://images.pexels.com/photos/1098592/pexels-photo-1098592.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "American", "category": "Deserts", "waiting":15},
    {"name": "Taco chips", "price": 400, "image_url": "https://images.pexels.com/photos/6004182/pexels-photo-6004182.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2", "cuisine": "Mexican", "category": "Starter", "description": "Perfectly crisp, homade mexican snacks with a side guacamole and secret ranch sauce", "waiting":10},
    {"name": "Egg rolls", "price": 300, "image_url": "https://img.freepik.com/free-photo/deep-fried-spring-rolls_1388-95.jpg?t=st=1740056520~exp=1740060120~hmac=193fbce88a676a8a0a9322f0b236c5796679b40c6b58df71a5c60f326045f675&w=1060", "cuisine": "Chinese", "category": "Snacks", "description": "Lovely Chinese egg rolls deep fried to perfection with egg and cheese fillings","waiting":7},
]

order_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
payment_methods = ["Apple Pay", "M-Pesa", "Cash", "Card"]

with app.app_context():
    db.drop_all()
    db.create_all()
   
    print("Database reset complete.")

    
    users = [User(**data) for data in user_data]
    db.session.add_all(users)
    db.session.commit()
    
    owners = User.query.filter_by(role='Owner').all()
    customers = User.query.filter_by(role='Customer').all()

    for outlet in outlet_data:
        stmt = insert(Outlet).values(
            name=outlet["name"],
            image_url=outlet["image_url"],
            owner_id=random.choice(owners).id  # Assign random owner
        ).on_conflict_do_nothing(index_elements=["name"])  # Prevent duplicates

        db.session.execute(stmt)
    db.session.commit()
    print("Outlets inserted without duplicates!")

    outlets = Outlet.query.all()

    menu_items = []
    menu_items = []
    for outlet in outlets:
        for category, items in outlet["menus"].items():
            for menu_item in items:
                menu_item_db = MenuItem(
                    name=menu_item["name"],
                    price=menu_item["price"],
                    image_url=menu_item["image_url"],
                    cuisine=menu_item["cuisine"],
                    category=category,
                    waiting=menu_item["waiting"],
                    outlet_id=outlet.id
                )
                menu_items.append(menu_item_db)

    db.session.add_all(menu_items)
    db.session.commit()
    print("Database seeded successfully with Menu Items data!")

    owner_menus = []
    for owner in owners:
        outlet = random.choice(outlets)
        outlet_menu_items = [item for item in menu_items if item.outlet_id == outlet.id]

        for menu_item in outlet_menu_items:
            owner_menu = OwnerMenu(
                owner_id=owner.id,
                outlet_id=outlet.id,
                name=menu_item.name,
                price=menu_item.price,
                image_url=menu_item.image_url,
                cuisine=menu_item.cuisine,
                category=menu_item.category,
                waiting=menu_item.waiting
            )
            owner_menus.append(owner_menu)

    db.session.add_all(owner_menus)
    db.session.commit()
    print("Database seeded successfully with OwnerMenu data!")

    print("\n--- Outlets and Their Menus ---\n")
    for outlet in outlets:
        print(f"Outlet: {outlet.name}")
        menu_items = MenuItem.query.filter_by(outlet_id=outlet.id).all()

        if menu_items:
            for item in menu_items:
                print(f" - {item.name}: {item.price} Ksh")
        else:
            print(" - No menu items available.")
        
        print("\n")
      
    orders = []
    for customer in customers:
        num_orders = random.randint(1, 5)  # Each customer places 1-5 orders
        for _ in range(num_orders):
            order = Order(
                customer_id=customer.id,
                outlet_id=random.choice(outlets).id,
                status=random.choice(order_statuses),
                table_number=random.randint(1, 20)
            )
            orders.append(order)

    db.session.add_all(orders)
    db.session.commit()
    print(f"Database seeded successfully with {len(orders)} Orders!")

    
    order_items = []
    for order in orders:
        # Add items to the order
        for _ in range(random.randint(1, 5)):
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=random.choice(menu_items).id,
                quantity=random.randint(1, 20),
                payment_method=random.choice(payment_methods)
            )
            menu_item = MenuItem.query.get(order_item.menu_item_id)
            total_price = float(menu_item.price) * order_item.quantity

            order_item.total_price = total_price

            order_items.append(order_item)

        order_total = sum([float(item.total_price) for item in order.order_items])
        order.total_price = order_total

    db.session.add_all(order_items)
    db.session.commit()
    print("Database seeded successfully with Order Items data!")


    
    bookings = []
    for _ in range(10):
        booking_time = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 10), hours=random.randint(1, 24))
        booking = TableBooking(
            customer_id=random.choice(customers).id,
            table_number=random.randint(1, 20),
            booking_time=booking_time
        )
        bookings.append(booking)
    db.session.add_all(bookings)
    db.session.commit()
    print("Database seeded successfully with Table bookings data!")

    
    print("Database seeded successfully!")