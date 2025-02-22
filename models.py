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
            'category': self.category
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
        orders = relationship('OrderItem', back_populates='menu_item')
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
                'description':self.description,
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

    outlet = db.relationship('Outlet', back_populates='orders')
    customer = db.relationship('User', back_populates='orders')
    table_booking = db.relationship('TableBooking', back_populates='orders', overlaps="orders")
    order_items = db.relationship('OrderItem', back_populates='order')
    

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
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'outlet_id': self.outlet_id,
            'table_booking_id': self.table_booking_id,
            'table_number': self.table_number,
            'status': self.status,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat(),
            'order_items': [item.to_dict() for item in self.order_items]
        }


class OrderItem(db.Model):
    __tablename__ = 'orderitem'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menuitem.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String, nullable=False)
    total_price = deferred(db.Column(db.Float, nullable=False))


    order = db.relationship('Order', back_populates='order_items')
    menu_item = db.relationship('MenuItem', back_populates='orders')

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        return quantity

    def to_dict(self):
        return{
            'id': self.id,
            'order_id': self.order_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name,
            'image_url': self.menu_item.image_url, 
            'quantity': self.quantity,
            'payment_method': self.payment_method,
            'total_price': self.total_price
    }

@event.listens_for(OrderItem, 'before_insert')
@event.listens_for(OrderItem, 'before_update')
def set_total_price(mapper, connection, target):
    menu_item = db.session.get(MenuItem, target.menu_item_id)
    if menu_item and target.total_price is None:  # Prevent unnecessary updates
        target.total_price = target.quantity * menu_item.price


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