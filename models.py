from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship,validates
from datetime import datetime, timezone
import re

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  

    outlets = relationship('Outlet', back_populates='owner', lazy=True)
    orders = relationship('Order', backref='customer', lazy=True)
    bookings = relationship('TableBooking', backref='customer', lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r'^\S+@\S+\.\S+$', email):
            raise ValueError("Invalid email format")
        return email

    @validates('role')
    def validate_role(self, key, role):
        valid_roles = ['customer', 'owner']
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        return role


class OwnerMenu(db.Model):
    __tablename__ = 'ownermenu'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String, nullable=True)
    cuisine = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    waiting = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'), nullable=False)

    owner = db.relationship('User', backref='owner_menus')
    outlet = db.relationship('Outlet', back_populates='owner_menus')
    menu_item = db.relationship('MenuItem', back_populates='owner_menu')

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'outlet_id': self.outlet_id,
            'name': self.name,
            'price': self.price,
            'image': self.image,
            'cuisine': self.cuisine,
            'category': self.category
        }


class Outlet(db.Model):
    __tablename__ = 'outlet'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_url= db.Column(db.String, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    menu_items = relationship('MenuItem', back_populates='outlet', lazy=True)
    orders = relationship('Order', backref='outlet', lazy=True)
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
    category = db.Column(db.String(50), nullable=False)
    waiting = db.Column(db.Integer, nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'), nullable=False)
    owner_menu_id= db.Column(db.Integer, db.ForeignKey('ownermenu.id'), nullable=True)

    outlet = db.relationship('Outlet', back_populates='menu_items')
    orders = relationship('OrderItem', back_populates='menu_item')
    owner_menu = relationship('OwnerMenu', back_populates='menu_item', uselist=False)

    @validates('price')
    def validate_price(self, key, price):
        if price <= 0:
            raise ValueError("Price must be a positive number")
        return price


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlet.id'), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    table_number = db.Column(db.Integer, nullable=False)

    order_items = relationship('OrderItem', back_populates='order')

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
        return status

    @validates('table_number')
    def validate_table_number(self, key, table_number):
        if table_number < 1:
            raise ValueError("Table number must be a positive integer")
        return table_number


class OrderItem(db.Model):
    __tablename__ = 'orderitem'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menuitem.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String, nullable=False)

    order = relationship('Order', back_populates='order_items')
    menu_item = relationship('MenuItem', back_populates='orders')

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        return quantity


class TableBooking(db.Model):
    __tablename__ = 'tablebooking'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    table_number = db.Column(db.Integer, nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.now(timezone.utc)) 

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
    
