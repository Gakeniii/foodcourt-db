#!/usr/bin/env python3

import os

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from dotenv import load_dotenv
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import MetaData
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity)

load_dotenv()

from models import db, User, OwnerMenu, Outlet, MenuItem, Order, TableBooking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8) 
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30) 
app.json.compact = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

CORS(app,  supports_credentials=True)


class UserResource(Resource):
    @jwt_required()
    def get(self, user_id=None):
        if user_id is None:
            users = User.query.all()
            return jsonify([
                {"id": user.id, "name": user.name, "role": user.role, "password": user.password}
                for user in users
            ])

        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'password': user.password
        }

        if user.role == 'Owner':
            user_data['outlets'] = [
                {
                    'id': outlet.id,
                    'name': outlet.name,
                    'menu_items': [
                        {'id': item.id, 'name': item.name, 'price': item.price}
                        for item in outlet.menu_items
                    ]
                } for outlet in user.outlets
            ]
        elif user.role == 'Customer':
            user_data.update({
                'orders': [
                    {'id': order.id, 'status': order.status}
                    for order in user.orders
                ],
                'bookings': [
                    {'id': booking.id, 'table_number': booking.table_number}
                    for booking in user.bookings
                ]
            })

        return jsonify(user_data)

    @jwt_required()
    def patch(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        for key, value in data.items():
            setattr(user, key, value)

        db.session.commit()
        return jsonify({
            'name': user.name,
            'email': user.email,
            'role': user.role,
        })

    # @jwt_required()
    # def delete(self, user_id):
    #     user = User.query.get_or_404(user_id)

    #     # Manually delete related records
    #     Order.query.filter_by(user_id=user.id).delete()
    #     TableBooking.query.filter_by(customer_id=user.id).delete()
    #     Outlet.query.filter_by(owner_id=user.id).delete()

    #     db.session.delete(user)
    #     db.session.commit()

    #     return jsonify({'message': 'User deleted successfully'})


class AuthResource(Resource):
    def post(self, action):
        data = request.get_json()

        if action == "signup":
            if User.query.filter_by(email=data["email"]).first():
                return {"error": "User already exists"}, 400

            hashed_password = generate_password_hash(data["password"])
            user = User(
                name=data["name"],
                email=data["email"],
                password=hashed_password,
                role=data["role"]
            )

            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity={"id": user.id, "role": user.role, "email": user.email})
            refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role, "email": user.email})

            return {
                "message": "User created successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"id": user.id, "name": user.name, "role": user.role}
            }, 201

        elif action == "login":
            user = User.query.filter_by(email=data["email"]).first()
            if not user or not check_password_hash(user.password, data["password"]):
                return {"error": "Invalid email or password"}, 401

            access_token = create_access_token(identity={"id": user.id, "role": user.role, "email": user.email})
            refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role, "email": user.email})
            return {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"id": user.id, "name": user.name, "role": user.role}
            }, 200
        
class RefreshTokenResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}, 200

api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(AuthResource, "/api/auth/<string:action>")
api.add_resource(RefreshTokenResource, "/api/auth/refresh")

class OutletResource(Resource):
    def get(self, outlet_id=None):

        cuisine_filter = request.args.get("cuisine", None)
        if outlet_id is None:
            outlets = Outlet.query.all()

            outlet_list = []
            for outlet in outlets:
                cuisines = list(set(item.cuisine for item in outlet.menu_items))

                if cuisine_filter and cuisine_filter not in cuisines:
                    continue

                outlet_list.append({
                    'id': outlet.id,
                    'image_url': outlet.image_url,
                    'name': outlet.name,
                    'owner_id': outlet.owner_id,
                    'owner_name': outlet.owner.name if outlet.owner and outlet.owner.role == 'Owner' else None,
                    'cuisines': cuisines,  # Include cuisines in the response
                    'menu_items': [{
                        'id': item.id,
                        'name': item.name,
                        'image_url': item.image_url,
                        'category': item.category,
                        'cuisine': item.cuisine,
                        'description': item.description,
                        'price': item.price,
                        'waiting': item.waiting
                    } for item in outlet.menu_items],
                    'orders': [{'id': order.id, 'status': order.status} for order in outlet.orders]
                })

            return jsonify(outlet_list)
        
        outlet = Outlet.query.get(outlet_id)
        if not outlet:
            return {"error": "Outlet not found"}, 404

        return jsonify({
            'id': outlet.id,
            'image_url': outlet.image_url,
            'name': outlet.name,
            'owner_id': outlet.owner_id,
            'owner_name': outlet.owner.name if outlet.owner and outlet.owner.role == 'Owner' else None,
            'cuisines': list(set(item.cuisine for item in outlet.menu_items)),  # Unique cuisines
            'menu_items': [{
                'id': item.id,
                'name': item.name,
                'image_url': item.image_url,
                'category': item.category,
                'cuisine': item.cuisine,
                'description': item.description,
                'waiting': item.waiting,
                'price': item.price,
            } for item in outlet.menu_items],
            'orders': [{'id': order.id, 'status': order.status} for order in outlet.orders]
        })

    def post(self):
        data = request.get_json()

        owner = User.query.get(data.get('owner_id'))
        if not owner or owner.role != 'Owner':
            return jsonify({'error': 'Invalid owner id. User must have role "Owner".'}), 400
        
        outlet = Outlet(name=data['name'], owner_id=data['owner_id'], image_url=data['image_url'])
        db.session.add(outlet)
        db.session.commit()

        return jsonify({
            'message': 'Outlet created successfully',
            'id': outlet.id,
            'image_url': outlet.image_url,
            'name': outlet.name,
            'owner_id': outlet.owner_id,
            'owner_name': outlet.owner.name if outlet.owner and outlet.owner.role == 'Owner' else None
        })
    
    def patch(self, outlet_id):
        outlet = Outlet.query.get_or_404(outlet_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(outlet, key, value)
        db.session.commit()
        return jsonify({
            'message': 'Outlet updated successfully',
            'id': outlet.id,
            'name': outlet.name,
            'owner_id': outlet.owner_id,
            'owner_name': outlet.owner.name if outlet.owner and outlet.owner.role == 'Owner' else None
            })
    
    def delete(self, outlet_id):
        outlet = Outlet.query.get_or_404(outlet_id)
        db.session.delete(outlet)
        db.session.commit()
        return jsonify({'message': 'Outlet deleted successfully'})

api.add_resource(OutletResource, '/outlets', '/outlets/<int:outlet_id>')


class MenuItemResource(Resource):
    def get(self, menu_item_id=None):
        if menu_item_id is None:
            menu_items = MenuItem.query.all()
            return [
                {
                    'id': item.id,
                    'name': item.name,
                    'image_url': item.image_url,
                    'price': int(item.price),  
                    'cuisine': item.cuisine,
                    'category': item.category,
                    'description':item.description,
                    'waiting': item.waiting,
                    'outlet': {'id': item.outlet.id, 'name': item.outlet.name} if item.outlet else None
                } for item in menu_items
            ]

        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {"error": "Menu item not found"}, 404 

        return {
            'id': menu_item.id,
            'name': menu_item.name,
            'image_url': menu_item.image_url,
            'price': int(menu_item.price),
            'cuisine': menu_item.cuisine,
            'category': menu_item.category,
            'description':menu_item.description,
            'waiting': menu_item.waiting,
            'outlet': {'id': menu_item.outlet.id, 'name': menu_item.outlet.name} if menu_item.outlet else None
        }

    def post(self):
        data = request.get_json()

        if 'outlet_id' not in data or data['outlet_id'] is None:
            return {"error": "Outlet ID is required"}, 400

        try:
            data['price'] = int(data['price'])

            outlet = Outlet.query.get(data['outlet_id'])
            if not outlet:
                return {"error": "Outlet not found"}, 404

            owner_menu = OwnerMenu.query.filter_by(outlet_id=outlet.id).first()

            if not owner_menu:
                return {"error": "Owner menu not found for this outlet"}, 404

            
            menu_item = MenuItem(
                name=data['name'],
                image_url=data.get('image_url'),
                price=data['price'],  
                cuisine=data['cuisine'],
                category=data.get('category'),
                description=data.get('description'),
                waiting=data['waiting'],
                outlet_id=outlet.id,
                owner_menu_id=owner_menu.id 
            )

            db.session.add(menu_item)
            db.session.commit()

            return {"message": "Menu item created successfully", "id": menu_item.id}, 201

        except ValueError:
            return {"error": "Invalid price format. Must be a whole number."}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    
    def patch(self, menu_item_id):
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(menu_item, key, value)
        db.session.commit()
        return jsonify({'message': 'Menu item updated successfully'})
    
    def delete(self, menu_item_id):
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        db.session.delete(menu_item)
        db.session.commit()
        return jsonify({'message': 'Menu item deleted successfully'})

api.add_resource(MenuItemResource, '/menu_items', '/menu_items/<int:menu_item_id>')



class OrderResource(Resource):
    def get(self, order_id=None):
        if order_id is None:
            orders = Order.query.all()
            return jsonify([order.to_dict() for order in orders])

        order = Order.query.get(order_id)
        if not order:
            return {"error": "Order not found"}, 404

        return jsonify(order.to_dict())


    def post(self):
        data = request.get_json()
        customer_id = data.get('customer_id')
        outlet_id = data.get('outlet_id')
        table_booking_id = data.get('table_booking_id')  # Optional
        table_number = data.get('table_number')  # Optional
        order_items_data = data.get('order_items')  # List of order items (menu item ids and quantities)

        # if not order_items_data or not isinstance(order_items_data, list):
        #     return {"error": "Order items are required and must be a list."}, 400
        if TableBooking.query.filter_by(table_number=table_number).first():
            return {"error": "Table already booked"}, 400
        

        # Check if customer_id exists in the User table
        # try:
        #     customer = User.query.filter_by(id=customer_id).one()
        # except NoResultFound:
        #     return {"error": "Customer not found"}, 404

        new_order = Order(
            customer_id=customer_id,
            outlet_id=outlet_id,
            table_booking_id=table_booking_id,
            table_number=table_number,
            order_items=[]  # Initialize empty
        )

        total_price = 0
        for item_data in order_items_data:
            menu_item = MenuItem.query.get(item_data.get('menu_item_id'))
            if not menu_item:
                return {"error": f"Menu item {item_data.get('menu_item_id')} not found"}, 404

            quantity = item_data.get('quantity', 1)
            payment_method = item_data.get('payment_method', "Cash")
            new_order.add_order_item(menu_item.id, quantity, payment_method)
            total_price += menu_item.price * quantity

        db.session.add(new_order)
        db.session.commit()

        return {
            "message": "Order created successfully",
            "order_id": new_order.id,
            "total_price": new_order.total_price
        }, 201


    def patch(self, order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json()

        # valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
        # if "status" in data and data["status"] not in valid_statuses:
        #     return {"error": "Invalid status. Allowed values: 'Pending', 'Confirmed', 'Completed', 'Cancelled'"}, 400

        if "order_items" in data:
            order.order_items = []  # Clear existing items
            total_price = 0
            for item_data in data["order_items"]:
                menu_item = MenuItem.query.get(item_data.get("menu_item_id"))
                if not menu_item:
                    return {"error": f"Menu item {item_data.get('menu_item_id')} not found"}, 404
                quantity = item_data.get("quantity", 1)
                payment_method = item_data.get("payment_method", "Cash")
                order.add_order_item(menu_item.id, quantity, payment_method)
                total_price += menu_item.price * quantity

            order.total_price = total_price  # Update total price
        
        for key, value in data.items():
            if key != "order_items":
                setattr(order, key, value)

        db.session.commit()
        return jsonify({"message": "Order updated successfully", "updated_order": order.to_dict()})

    def delete(self, order_id):
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"})

api.add_resource(OrderResource, '/orders', '/orders/<int:order_id>')


class TableBookingResource(Resource):
    def get(self, booking_id=None):
        if booking_id is None:
            bookings = TableBooking.query.all()
            return jsonify([
                {
                    'id': booking.id,
                    'customer_id': booking.customer_id,
                    'customer_name': booking.customer.name if booking.customer else "Unknown",
                    'customer_email': booking.customer.email if booking.customer else "Unknown",
                    'customer_role': booking.customer.role if booking.customer else "Unknown",
                    'table_number': booking.table_number,
                    'booking_time': booking.booking_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'created_at': booking.created_at.strftime("%Y-%m-%d %H:%M:%S") if booking.created_at else None,
                    'availability': booking.available  
                } for booking in bookings
            ])
        
        booking = TableBooking.query.get(booking_id)
        if not booking:
            return {"error": "Booking not found"}, 404

        # ** Set availability to False when a booking is retrieved **
        if booking.available:  
            booking.available = False
            db.session.commit()

        return jsonify({
            'id': booking.id,
            'customer_id': booking.customer_id,
            'customer_name': booking.customer.name if booking.customer else "Unknown",
            'customer_email': booking.customer.email if booking.customer else "Unknown",
            'table_number': booking.table_number,
            'booking_time': booking.booking_time.strftime("%Y-%m-%d %H:%M:%S"),
            'created_at': booking.created_at.strftime("%Y-%m-%d %H:%M:%S") if booking.created_at else None,
            'availability': booking.available 
        })

    def post(self):
        data = request.get_json()

        try:
            if 'booking_time' not in data:
                return jsonify({"error": "Booking time is required"}), 400

            booking_time = datetime.fromisoformat(data['booking_time'])

            if booking_time.tzinfo is None:
                booking_time = booking_time.replace(tzinfo=timezone.utc)

            if booking_time <= datetime.now(timezone.utc):
                return jsonify({"error": "Booking time must be in the future"}), 400
            
            data['booking_time'] = booking_time

        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DDTHH:MM:SS or include timezone"}), 400

        booking = TableBooking(**data)
        booking.available = False  
        db.session.add(booking)
        db.session.commit()

        return {'message': 'Table booking created successfully', 'booking_id': booking.id}, 201

    def delete(self, booking_id):
        booking = TableBooking.query.get_or_404(booking_id)
        booking.available = True  # Mark table as available again upon deletion
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Table booking deleted successfully'})

api.add_resource(TableBookingResource, '/bookings', '/bookings/<int:booking_id>')


class UnbookedTablesResource(Resource):
    def get(self):
        try:
            all_table_numbers = set(range(1, 21))

            booked_tables = db.session.query(TableBooking.table_number).distinct().all()
            booked_tables = {table[0] for table in booked_tables}

            unbooked_tables = all_table_numbers - booked_tables

            return jsonify({"unbooked_tables": list(unbooked_tables)})

        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(UnbookedTablesResource, '/available', endpoint="available")



class OwnerMenuResource(Resource):
    def get(self):
        menus = MenuItem.query.all()
        return jsonify([menu.to_dict() for menu in menus])

    def post(self):
        data = request.get_json()

        if 'outlet_id' not in data or data['outlet_id'] is None:
            return {"error": "Outlet ID is required"}, 400
        if 'waiting' not in data or data['waiting'] is None:
            return {"error": "Waiting time is required"}, 400

        try:
            data['price'] = int(data['price'])
            data['waiting'] = int(data['waiting'])  # Ensure waiting is an integer

            outlet = Outlet.query.get(data['outlet_id'])
            if not outlet:
                return {"error": "Outlet not found"}, 404

            menu_item = MenuItem(
                name=data['name'],
                image_url=data.get('image_url'),
                price=data['price'],  
                cuisine=data['cuisine'],
                category=data.get('category'),
                description=data.get('description'),
                waiting=data['waiting'],  # Ensure it has a valid value
                outlet_id=data['outlet_id'],
                owner_menu_id=data.get('owner_menu_id')  # Optional but should be valid if provided
            )

            db.session.add(menu_item)
            db.session.commit()

            return {"message": "Menu item created successfully", "id": menu_item.id}, 201

        except ValueError:
            return {"error": "Invalid price or waiting format. Must be a whole number."}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class SingleOwnerMenuResource(Resource):
    def get(self, menu_id):
        menu = MenuItem.query.get(menu_id)
        if not menu:
            return {"message": "Menu item not found"}, 404
        return jsonify(menu.to_dict())

    def patch(self, menu_id):
        menu = MenuItem.query.get(menu_id)
        if not menu:
            return {"message": "Menu item not found"}, 404

        data = request.get_json()

        menu.name = data.get('name', menu.name)
        menu.price = data.get('price', menu.price)
        menu.image_url = data.get('image_url', menu.image_url)
        menu.cuisine = data.get('cuisine', menu.cuisine)
        menu.category = data.get('category', menu.category)
        menu.waiting = data.get('waiting', menu.waiting)

        db.session.commit()

        menu_item = MenuItem.query.filter_by(owner_menu_id=menu.id).first()
        if menu_item:
            menu_item.name = menu.name
            menu_item.price = menu.price
            menu_item.image_url = menu.image_url
            menu_item.cuisine = menu.cuisine
            menu_item.category = menu.category
            db.session.commit()

        return {"message": "Menu item updated successfully", "menu": menu.to_dict()}

    def delete(self, menu_id):
        menu = MenuItem.query.get(menu_id)
        if not menu:
            return {"message": "Menu item not found"}, 404

        db.session.delete(menu)
        db.session.commit()

        MenuItem.query.filter_by(owner_menu_id=menu_id).delete()
        db.session.commit()

        return {"message": "Menu item deleted successfully"}, 200
    
api.add_resource(OwnerMenuResource,'/ownermenu')
api.add_resource(SingleOwnerMenuResource,'/ownermenu/<int:menu_id>')  