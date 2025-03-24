from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship,validates, deferred
from datetime import datetime, timezone
from sqlalchemy import event
from werkzeug.security import check_password_hash
from sqlalchemy.sql import func
import re

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  

    outlets = db.relationship('Outlet', back_populates='owner', lazy=True)
    orders = db.relationship('Order', back_populates='customer', lazy=True)
    bookings = db.relationship('TableBooking', back_populates='customer', lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r'^\S+@\S+\.\S+$', email):
            raise ValueError("Invalid email format")
        return email

    @validates('role')
    def validate_role(self, key, role):
        valid_roles = ['Customer', 'Owner']
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        return role
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class OwnerMenu(db.Model):
    __tablename__ = 'ownermenu'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String, nullable=True)
    cuisine = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=True)
    waiting = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'), nullable=False)

    owner = db.relationship('User', backref='owner_menus')
    outlet = db.relationship('Outlet', back_populates='owner_menus')
    menu_items = db.relationship('MenuItem', back_populates='owner_menu', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'outlet_id': self.outlet_id,
            'name': self.name,
            'price': self.price,
            'image_url': self.image_url,
            'cuisine': self.cuisine,
            'category': self.category,
            'description': self.description
        }


class Outlet(db.Model):
    __tablename__ = 'outlet'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_url= db.Column(db.String, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    menu_items = relationship('MenuItem', back_populates='outlet', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='outlet')
    owner_menus = db.relationship('OwnerMenu', back_populates='outlet')
    owner = db.relationship('User', back_populates='outlets')

    @property
    def owner_name(self):
        return self.owner.username if self.owner and self.owner.role == 'owner' else None
      

class MenuItem(db.Model):
        __tablename__ = 'menuitem'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        image_url = db.Column(db.String, nullable=True)
        price = db.Column(db.Integer, nullable=False) 
        cuisine = db.Column(db.String(50), nullable=False)
        description = db.Column(db.String, nullable=True)
        category = db.Column(db.String(50), nullable=False)
        waiting = db.Column(db.Integer, nullable=False)
        outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'), nullable=False)
        owner_menu_id= db.Column(db.Integer, db.ForeignKey('ownermenu.id'), nullable=True)

        outlet = db.relationship('Outlet', back_populates='menu_items')
        owner_menu = relationship('OwnerMenu', back_populates='menu_items')

        @validates('price')
        def validate_price(self, key, price):
            if price <= 0:
                raise ValueError("Price must be a positive number")
            return price
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'price': self.price,
                'image_url': self.image_url,
                'cuisine': self.cuisine,
                'category': self.category,
                'description': self.description,
                'waiting': self.waiting,
                'owner_menu_id': self.owner_menu_id
            }

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'), nullable=False)
    table_booking_id = db.Column(db.Integer, db.ForeignKey('table_bookings.id'), nullable=True)
    table_number = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="Pending")
    total_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=func.now())
    order_items = db.Column(db.JSON, nullable=False, default=[])

    outlet = db.relationship('Outlet', back_populates='orders')
    customer = db.relationship('User', back_populates='orders')
    table_booking = db.relationship('TableBooking', back_populates='orders', overlaps="orders")

    @validates('table_number')
    def validate_table_number(self, key, table_number):
        if table_number and (table_number < 1 or table_number > 20):
            raise ValueError("Invalid table number. Must be between 1 and 20.")
        return table_number

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
        if status not in valid_statuses:
            raise ValueError("Invalid status")
        return status

    def to_dict(self):
        from models import MenuItem

        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'outlet_id': self.outlet_id,
            'outlet_name': self.outlet.name if self.outlet else None,
            'table_booking_id': self.table_booking_id,
            'table_number': self.table_number,
            'status': self.status,
            'total_price': round(self.total_price, 2),
            'created_at': self.created_at.isoformat(),
            'order_items': [
                {
                    'menu_item_id': item['menu_item_id'],
                    'menu_item_name': db.session.get(MenuItem, item['menu_item_id']).name if db.session.get(MenuItem, item['menu_item_id']) else None,
                    'menu_item_price': db.session.get(MenuItem, item['menu_item_id']).price if db.session.get(MenuItem, item['menu_item_id']) else None,
                    'menu_item_image': db.session.get(MenuItem, item['menu_item_id']).image_url if db.session.get(MenuItem, item['menu_item_id']) else None,
                    'quantity': item['quantity'],
                    'payment_method': item['payment_method'],
                    'total_price': round(item['quantity'] * db.session.get(MenuItem, item['menu_item_id']).price, 2) if db.session.get(MenuItem, item['menu_item_id']) else None,
                }
                for item in self.order_items
            ]
        }

    def add_order_item(self, menu_item_id, quantity, payment_method):
        from models import MenuItem

        menu_item = db.session.get(MenuItem, menu_item_id)
        if not menu_item:
            raise ValueError("Menu item not found")

        item_total = round(quantity * menu_item.price, 2)

        order_item = {
            'menu_item_id': menu_item_id,
            'menu_item_name': menu_item.name,
            'image_url': menu_item.image_url,
            'quantity': quantity,
            'payment_method': payment_method,
            'total_price': item_total
        }

        self.order_items.append(order_item)
        self.total_price = sum(item['total_price'] for item in self.order_items)

@event.listens_for(Order, 'before_insert')
@event.listens_for(Order, 'before_update')
def set_total_price(mapper, connection, target):
    target.total_price = sum(item['total_price'] for item in target.order_items)


class TableBooking(db.Model):
    __tablename__ = 'table_bookings'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    table_number = db.Column(db.Integer, nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    available = db.Column(db.Boolean, default=True)

    customer = db.relationship('User', back_populates='bookings')
    orders = db.relationship('Order', back_populates='table_booking', overlaps="orders")

    @validates('table_number')
    def validate_table_number(self, key, table_number):
        if table_number < 1:
            raise ValueError("Table number must be a positive integer")
        return table_number

    @validates('booking_time')
    def validate_booking_time(self, key, booking_time):
        if booking_time <= datetime.now(timezone.utc):  
            raise ValueError("Booking time must be in the future")
 
        return booking_time 
    
    def to_dict(self):
        return {
            "booking_id": self.id,
            "table_number": self.table_number,
            # Use isoformat() to convert the datetime to an ISO 8601 string.
            "booking_time": self.booking_time.isoformat(),
            "available": self.available,
        }
