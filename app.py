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


if __name__ == '__main__':
    app.run(debug=True)
