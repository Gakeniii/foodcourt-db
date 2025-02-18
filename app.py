from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Routes for User
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user = User(name=data['name'], email=data['email'], password=hashed_password, role=data['role'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role})

# Routes for Outlet
@app.route('/outlets', methods=['POST'])
def create_outlet():
    data = request.json
    outlet = Outlet(name=data['name'], owner_id=data['owner_id'])
    db.session.add(outlet)
    db.session.commit()
    return jsonify({'message': 'Outlet created successfully'}), 201

@app.route('/outlets/<int:outlet_id>', methods=['GET'])
def get_outlet(outlet_id):
    outlet = Outlet.query.get_or_404(outlet_id)
    return jsonify({'id': outlet.id, 'name': outlet.name, 'owner_id': outlet.owner_id})

# Routes for MenuItem
@app.route('/menu-items', methods=['POST'])
def create_menu_item():
    data = request.json
    menu_item = MenuItem(name=data['name'], price=data['price'], category=data['category'], cuisine=data['cuisine'], outlet_id=data['outlet_id'])
    db.session.add(menu_item)
    db.session.commit()
    return jsonify({'message': 'Menu item created successfully'}), 201

@app.route('/menu-items/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return jsonify({'id': item.id, 'name': item.name, 'price': item.price, 'category': item.category, 'cuisine': item.cuisine, 'outlet_id': item.outlet_id})

# Routes for Order
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    order = Order(customer_id=data['customer_id'], outlet_id=data['outlet_id'], status='Pending')
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order created successfully'}), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({'id': order.id, 'customer_id': order.customer_id, 'outlet_id': order.outlet_id, 'status': order.status, 'created_at': order.created_at})

# Routes for Table Booking
@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    booking = TableBooking(customer_id=data['customer_id'], table_number=data['table_number'], booking_time=datetime.strptime(data['booking_time'], '%Y-%m-%d %H:%M:%S'))
    db.session.add(booking)
    db.session.commit()
    return jsonify({'message': 'Booking created successfully'}), 201

@app.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = TableBooking.query.get_or_404(booking_id)
    return jsonify({'id': booking.id, 'customer_id': booking.customer_id, 'table_number': booking.table_number, 'booking_time': booking.booking_time})

if __name__ == '__main__':
    app.run(debug=True)
