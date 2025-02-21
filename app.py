from flask import Flask, request, jsonify
from models import db, User, Outlet, MenuItem, Order, OrderItem, Table, Reservation
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_cors import CORS
from flask_restful import Api, Resource
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
app.config['SECRET_KEY'] = 'zdnksdghiosuvuksdhbvsmhdb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the app with db
db.init_app(app)

# Initialize extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt()
api = Api(app)
CORS(app, resources={r"*": {"origins": "*"}})
jwt = JWTManager(app)

# Register the Bcrypt instance with the Flask app
bcrypt.init_app(app)

# User registration form
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'customer')  # Default role is 'customer'

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    # Ensure password is a string
    password = str(password)

    # Hash the password before storing
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

# Login route that generates JWT token
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Convert pass to str before login
    password = str(password)

    # Find user by username
    user = User.query.filter_by(username=username).first()
    
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Create JWT token with user.id as string
    access_token = create_access_token(identity=str(user.id), fresh=True, expires_delta=timedelta(hours=1))  # token valid for 1 hour
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200

# Outlet Routes
@app.route('/outlets', methods=['POST'])
@jwt_required()  # This ensures that the user is authenticated
def create_outlet():
    # Get the current user from the JWT token
    current_user_id = get_jwt_identity()  # This gets the user ID from the JWT token
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role != 'true':
        return jsonify({"error": "You do not have the required permissions to create an outlet"}), 403

    data = request.json
    name = data.get('name')
    cuisine_type = data.get('cuisine_type')

    if not name or not cuisine_type:
        return jsonify({"error": "Name and cuisine type are required"}), 400

    # Create the outlet with the correct owner_id (as integer)
    new_outlet = Outlet(name=name, cuisine_type=cuisine_type, owner_id=current_user_id)
    db.session.add(new_outlet)
    db.session.commit()

    return jsonify({"message": "Outlet created successfully", "outlet_id": new_outlet.id}), 201

@app.route('/outlets/update/<int:outlet_id>', methods=['PUT'])
def update_outlet(outlet_id):
    data = request.json
    outlet = Outlet.query.get(outlet_id)

    if not outlet:
        return jsonify({"error": "Outlet not found"}), 404

    outlet.name = data.get('name', outlet.name)
    outlet.cuisine_type = data.get('cuisine_type', outlet.cuisine_type)
    db.session.commit()

    return jsonify({"message": "Outlet updated successfully"}), 200

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
    def get(self):
        birds = [bird.to_dict() for bird in User.query.all()]
        return make_response(jsonify(birds), 200)

# Table Routes
@app.route('/outlet/<int:outlet_id>/tables', methods=['POST'])
@jwt_required()
def create_table(outlet_id):
    # Get the current user from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the outlet exists and belongs to the current user
    outlet = Outlet.query.filter_by(id=outlet_id, owner_id=current_user_id).first()
    if not outlet:
        return jsonify({"error": "Outlet not found or you do not have permission to add tables to this outlet"}), 404

    data = request.get_json()
    table_number = data.get('table_number')
    is_available = data.get('is_available', 'true').lower() == 'true'  # Convert to boolean

    if not table_number:
        return jsonify({"error": "Table number is required"}), 400

    # Check if the table number is unique for the outlet
    existing_table = Table.query.filter_by(outlet_id=outlet_id, table_number=table_number).first()
    if existing_table:
        return jsonify({"error": "Table number already exists for this outlet"}), 400

    # Create the table
    new_table = Table(table_number=table_number, is_available=is_available, outlet_id=outlet_id)
    db.session.add(new_table)
    db.session.commit()

    return jsonify({"message": "Table created successfully", "table_id": new_table.id}), 201

# Menu Item Routes
@app.route('/outlet/<int:outlet_id>/menu-items', methods=['POST'])
@jwt_required()
def create_menu_item(outlet_id):
    # Get the current user from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the outlet exists and belongs to the current user
    outlet = Outlet.query.filter_by(id=outlet_id, owner_id=current_user_id).first()
    if not outlet:
        return jsonify({"error": "Outlet not found or you do not have permission to add menu items to this outlet"}), 404

    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    category = data.get('category')

    if not name or not price or not category:
        return jsonify({"error": "Name, price, and category are required"}), 400

    # Create the menu item
    new_menu_item = MenuItem(name=name, price=price, category=category, outlet_id=outlet_id)
    db.session.add(new_menu_item)
    db.session.commit()

    return jsonify({"message": "Menu item created successfully", "menu_item_id": new_menu_item.id}), 201

# Customer Routes

# Book a Table
@app.route('/outlet/<int:outlet_id>/book-table', methods=['POST'])
@jwt_required()
def book_table(outlet_id):
    # Get the current user from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the outlet exists
    outlet = Outlet.query.get(outlet_id)
    if not outlet:
        return jsonify({"error": "Outlet not found"}), 404

    data = request.get_json()
    table_id = data.get('table_id')
    reservation_time = data.get('reservation_time')

    if not table_id or not reservation_time:
        return jsonify({"error": "Table ID and reservation time are required"}), 400

    # Check if the table exists and is available
    table = Table.query.filter_by(id=table_id, outlet_id=outlet_id, is_available=True).first()
    if not table:
        return jsonify({"error": "Table not found or not available"}), 404

    # Convert reservation_time to datetime object
    try:
        reservation_time = datetime.fromisoformat(reservation_time)
    except ValueError:
        return jsonify({"error": "Invalid reservation time format. Use ISO format (e.g., YYYY-MM-DDTHH:MM:SS)"}), 400

    # Create the reservation
    new_reservation = Reservation(
        customer_id=current_user_id,
        table_id=table_id,
        reservation_time=reservation_time
    )
    db.session.add(new_reservation)
    db.session.commit()

    # Mark the table as unavailable
    table.is_available = False
    db.session.commit()

    return jsonify({"message": "Table booked successfully", "reservation_id": new_reservation.id}), 201

@app.route('/reservation/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(reservation_id):
    # Get the current user from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Find the reservation
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    # Debugging: Print reservation owner and current user
    print(f"Reservation Owner ID: {reservation.customer_id}")
    print(f"Current User ID: {current_user_id}")
    print(f"User Role: {user.role}")

    # Check if the current user is the owner of the reservation or an admin
    if reservation.customer_id != current_user_id and user.role != 'admin':
        print("Permission denied: User is not the owner or an admin")
        return jsonify({"error": "You do not have permission to delete this reservation"}), 403

    # Hard delete the reservation
    db.session.delete(reservation)
    db.session.commit()

    return jsonify({"message": "Reservation deleted successfully"}), 200

# View Menu for an Outlet
@app.route('/outlet/<int:outlet_id>/menu', methods=['GET'])
@jwt_required()
def view_menu(outlet_id):
    # Check if the outlet exists
    outlet = Outlet.query.get(outlet_id)
    if not outlet:
        return jsonify({"error": "Outlet not found"}), 404

    # Fetch all menu items for the outlet
    menu_items = MenuItem.query.filter_by(outlet_id=outlet_id).all()
    return jsonify([{
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "category": item.category
    } for item in menu_items]), 200

# Place an Order
@app.route('/outlet/<int:outlet_id>/place-order', methods=['POST'])
@jwt_required()
def place_order(outlet_id):
    # Get the current user from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the outlet exists
    outlet = Outlet.query.get(outlet_id)
    if not outlet:
        return jsonify({"error": "Outlet not found"}), 404

    data = request.get_json()
    reservation_id = data.get('reservation_id')
    items = data.get('items')  # List of {menu_item_id, quantity}

    if not items:
        return jsonify({"error": "Items are required"}), 400

    # Check if the reservation exists and belongs to the customer
    if reservation_id:
        reservation = Reservation.query.filter_by(id=reservation_id, customer_id=current_user_id).first()
        if not reservation:
            return jsonify({"error": "Reservation not found or does not belong to you"}), 404

    # Create the order
    new_order = Order(
        customer_id=current_user_id,
        outlet_id=outlet_id,
        reservation_id=reservation_id,
        status="pending"
    )
    db.session.add(new_order)
    db.session.commit()

    # Add order items
    for item in items:
        menu_item_id = item.get('menu_item_id')
        quantity = item.get('quantity')

        if not menu_item_id or not quantity:
            return jsonify({"error": "Menu item ID and quantity are required for each item"}), 400

        # Check if the menu item exists
        menu_item = MenuItem.query.filter_by(id=menu_item_id, outlet_id=outlet_id).first()
        if not menu_item:
            return jsonify({"error": f"Menu item with ID {menu_item_id} not found"}), 404

        # Create order item
        new_order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=menu_item_id,
            quantity=quantity
        )
        db.session.add(new_order_item)

    db.session.commit()

    return jsonify({"message": "Order placed successfully", "order_id": new_order.id}), 201

if __name__ == '__main__':
    app.run(debug=True)
