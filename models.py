from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # e.g., "customer", "outlet_owner"

class Outlet(db.Model):
    __tablename__ = 'outlets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    cuisine_type = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Table(db.Model):
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlets.id', name='fk_table_outlet'), nullable=False)

    # Define relationship to Outlet
    outlet = db.relationship('Outlet', backref='tables', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_reservation_customer'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id', name='fk_reservation_table'), nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', name='fk_reservation_order'), nullable=True)

    # Define relationship to Table
    table = db.relationship('Table', backref='reservations', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_order_customer'), nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlets.id', name='fk_order_outlet'), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id', name='fk_order_reservation'), nullable=True)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationship to OrderItem
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', name='fk_order_item_order'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', name='fk_order_item_menu_item'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    outlet_id = db.Column(db.Integer, db.ForeignKey('outlets.id', name='fk_menu_item_outlet'), nullable=False)
