#!/usr/bin/env python3

import os

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from dotenv import load_dotenv
from sqlalchemy import MetaData
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity)

load_dotenv()

from models import db, User, OwnerMenu, Outlet, MenuItem, Order, OrderItem, TableBooking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1) 
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=6) 
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
        if outlet_id is None:
            outlets = Outlet.query.all()
            return jsonify([
                {
                    'id': outlet.id,
                    'image_url': outlet.image_url,
                    'name': outlet.name,
                    'owner_id': outlet.owner_id,
                    'owner_name': outlet.owner.name if outlet.owner and outlet.owner.role == 'Owner' else None,  
                    'menu_items': [{'id': item.id, 'name': item.name} for item in outlet.menu_items],
                    'orders': [{'id': order.id, 'status': order.status} for order in outlet.orders]
                } for outlet in outlets
            ])
        
        outlet = Outlet.query.get(outlet_id)
        if not outlet:
            return {"error": "Outlet not found"}, 404
        
        return jsonify({
            'id': outlet.id,
            'image_url': outlet.image_url,
            'name': outlet.name,
            'owner_id': outlet.owner_id,
            'owner_name': outlet.owner.name if outlet.owner and outlet.owner.role == 'Owner' else None,
            'menu_items': [{'id': item.id, 'name': item.name} for item in outlet.menu_items],
            'orders': [{'id': order.id, 'status': order.status} for order in outlet.orders]
        })

    @jwt_required()
    def post(self):
            data = request.get_json()

            if not data or "owner_id" not in data:
                return {'error': 'Missing owner_id field'}, 400

            owner = User.query.get(data.get('owner_id'))
            if not owner:
                return {'error': 'Owner not found'}, 404
            elif owner.role != 'Owner':
                return {'error': 'User must have role "Owner"'}, 403

            outlet = Outlet(
                name=data['name'],
                owner_id=data['owner_id'],
                image_url=data.get('image_url', '')  # Default empty if image_url missing
            )

            db.session.add(outlet)
            db.session.commit()

            return {
                'message': 'Outlet created successfully',
                'id': outlet.id,
                'image_url': outlet.image_url,
                'name': outlet.name,
                'owner_id': outlet.owner_id,
                'owner_name': owner.name
            }, 201
    
    @jwt_required()
    def patch(self, outlet_id):
        outlet = Outlet.query.get_or_404(outlet_id)
        current_user = get_jwt_identity()

        if outlet.owner_id != current_user["id"]:
            return jsonify({'error': 'Unauthorized. You can only update your own outlets.'}), 403

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
    
    @jwt_required()
    def delete(self, outlet_id):
        outlet = Outlet.query.get_or_404(outlet_id)
        current_user = get_jwt_identity()

        if outlet.owner_id != current_user["id"]:
            return {'error': 'Unauthorized. You can only delete your own outlets.'}, 403

        db.session.delete(outlet)
        db.session.commit()
        return {'message': 'Outlet deleted successfully'}

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
                    'description': item.description,
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
            'description': menu_item.description,
            'waiting': menu_item.waiting,
            'outlet': {'id': menu_item.outlet.id, 'name': menu_item.outlet.name} if menu_item.outlet else None
        }

    @jwt_required()
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

    @jwt_required()
    def patch(self, menu_item_id):
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(menu_item, key, value)
        db.session.commit()
        return jsonify({'message': 'Menu item updated successfully'})
    
    @jwt_required()
    def delete(self, menu_item_id):
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        db.session.delete(menu_item)
        db.session.commit()
        return jsonify({'message': 'Menu item deleted successfully'})

api.add_resource(MenuItemResource, '/menu_items', '/menu_items/<int:menu_item_id>')


from flask_jwt_extended import jwt_required

class OrderResource(Resource):
    def get(self, order_id=None):
        if order_id is None:
            orders = Order.query.all()
            return jsonify([
                {
                    'id': order.id,
                    'customer_id': order.customer_id,
                    'customer_name': order.customer.name if order.customer else "Unknown",
                    'outlet_id': order.outlet_id,
                    'outlet_name': order.outlet.name if order.outlet else "Unknown",
                    'status': order.status,
                    'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'table_number': order.table_booking.table_number if order.table_booking else order.table_number
                } for order in orders
            ])

        order = Order.query.get(order_id)
        if not order:
            return {"error": "Order not found"}, 404

        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'customer_name': order.customer.name if order.customer else "Unknown",
            'outlet_id': order.outlet_id,
            'outlet_name': order.outlet.name if order.outlet else "Unknown",
            'status': order.status,
            'created_at': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'table_number': order.table_booking.table_number if order.table_booking else order.table_number
        })

    @jwt_required()  
    def post(self):
        data = request.get_json()
        customer_id = data.get('customer_id')
        outlet_id = data.get('outlet_id')
        status = data.get('status', "Pending")
        table_booking_id = data.get('table_booking_id')  # Optional
        table_number = data.get('table_number')  # Optional

        customer = User.query.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}, 404

        existing_booking = TableBooking.query.filter_by(customer_id=customer_id).first()
        
        if existing_booking:
            table_booking_id = existing_booking.id
            table_number = existing_booking.table_number
        elif table_number:  
            if TableBooking.query.filter_by(table_number=table_number).first():
                return {"error": "This table is already booked"}, 400
        else:
            return {"error": "Please provide a valid table number or book in advance"}, 400

        valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
        if status not in valid_statuses:
            return {"error": "Invalid status. Allowed values: 'Pending', 'Confirmed', 'Completed', 'Cancelled'"}, 404
        
        new_order = Order(
            customer_id=customer_id,
            outlet_id=outlet_id,
            table_booking_id=table_booking_id,
            table_number=table_number,
            status=status
        )

        db.session.add(new_order)
        db.session.commit()

        return {"message": "Order created successfully", "order_id": new_order.id}, 201
    
    @jwt_required()  
    def patch(self, order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json()

        valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
        if "status" in data and data["status"] not in valid_statuses:
            return {"error": "Invalid status. Allowed values: 'Pending', 'Confirmed', 'Completed', 'Cancelled'"}, 400
        
        for key, value in data.items():
            setattr(order, key, value)

        db.session.commit()
        return jsonify({'message': 'Order updated successfully', 'updated_order': order.status})

    @jwt_required()  
    def delete(self, order_id):
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'})
    
api.add_resource(OrderResource, '/orders', '/orders/<int:order_id>')


from flask_jwt_extended import jwt_required

class OrderItemResource(Resource):
    def get(self, order_item_id=None):
        if order_item_id is None:
            order_items = OrderItem.query.all()
            return jsonify([
                {
                    'id': item.id,
                    'order_id': item.order_id,
                    'menu_item_id': item.menu_item_id,
                    'menu_item_name': item.menu_item.name if item.menu_item else None, 
                    'quantity': item.quantity,
                    'payment_method': item.payment_method,
                    'order_details': {
                        'customer_id': item.order.customer_id if item.order else None,
                        'customer_name': item.order.customer.name if item.order and item.order.customer else None,
                        'outlet_id': item.order.outlet_id if item.order else None,
                        'outlet_name': item.order.outlet.name if item.order and item.order.outlet else None,
                        'status': item.order.status if item.order else None,
                        'table_number': item.order.table_number if item.order else None,
                        'created_at': item.order.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.order and item.order.created_at else None
                    }
                }
                for item in order_items
            ])

        order_item = OrderItem.query.get(order_item_id)
        if not order_item:
            return {"error": "Order item not found"}, 404

        return jsonify({
            'id': order_item.id,
            'order_id': order_item.order_id,
            'menu_item_id': order_item.menu_item_id,
            'menu_item_name': order_item.menu_item.name if order_item.menu_item else None,
            'quantity': order_item.quantity,
            'payment_method': order_item.payment_method,
            'order_details': {
                'customer_id': order_item.order.customer_id if order_item.order else None,
                'customer_name': order_item.order.customer.name if order_item.order and order_item.order.customer else None,
                'outlet_id': order_item.order.outlet_id if order_item.order else None,
                'outlet_name': order_item.order.outlet.name if order_item.order and order_item.order.outlet else None,
                'status': order_item.order.status if order_item.order else None,
                'table_number': order_item.order.table_number if order_item.order else None,
                'created_at': order_item.order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order_item.order and order_item.order.created_at else None
            }
        })

    @jwt_required()  
    def post(self):
        data = request.get_json()
        order_item = OrderItem(**data)
        db.session.add(order_item)
        db.session.commit()
        return jsonify({'message': 'Order item created successfully'})
    
    @jwt_required()  
    def patch(self, order_item_id):
        order_item = OrderItem.query.get_or_404(order_item_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(order_item, key, value)
        db.session.commit()
        return jsonify({'message': 'Order item updated successfully'})
    
    @jwt_required()  
    def delete(self, order_item_id):
        order_item = OrderItem.query.get_or_404(order_item_id)
        db.session.delete(order_item)
        db.session.commit()
        return jsonify({'message': 'Order item deleted successfully'})
    
api.add_resource(OrderItemResource, '/order_items', '/order_items/<int:order_item_id>')


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

        return jsonify({
            'id': booking.id,
            'customer_id': booking.customer_id,
            'customer_name': booking.customer.name if booking.customer else "Unknown",
            'customer_email': booking.customer.email if booking.customer else "Unknown",
            'customer_role': booking.customer.role if booking.customer else "Unknown",
            'table_number': booking.table_number,
            'booking_time': booking.booking_time.strftime("%Y-%m-%d %H:%M:%S"),
            'created_at': booking.created_at.strftime("%Y-%m-%d %H:%M:%S") if booking.created_at else None,
            'availability': booking.available 
        })

    def get_available_tables(self):
        available_tables = TableBooking.query.filter_by(availability=True).all()
        return jsonify([
            {
                'id': table.id,
                'table_number': table.table_number,
                'availability': table.available
            } for table in available_tables
        ])

    @jwt_required()
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

    @jwt_required()
    def delete(self, booking_id):
        booking = TableBooking.query.get_or_404(booking_id)
        booking.available = True  
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Table booking deleted successfully'})

api.add_resource(TableBookingResource, '/bookings', '/bookings/<int:booking_id>', '/bookings/available')


class OwnerMenuResource(Resource):
    def get(self):
        menus = OwnerMenu.query.all()
        return jsonify([
            {
                **menu.to_dict(),  # Include existing fields
                "owner_name": menu.owner.name if menu.owner else "Unknown"  # Add owner name
            }
            for menu in menus
        ])

    @jwt_required()  
    def post(self):
        data = request.get_json()

        if 'outlet_id' not in data or data['outlet_id'] is None:
            return {"error": "Outlet ID is required"}, 400
        if 'waiting' not in data or data['waiting'] is None:
            return {"error": "Waiting time is required"}, 400

        try:
            data['price'] = int(data['price'])
            data['waiting'] = int(data['waiting'])

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
                waiting=data['waiting'],
                outlet_id=data['outlet_id'],
                owner_menu_id=data.get('owner_menu_id')
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
        menu = OwnerMenu.query.get(menu_id)
        if not menu:
            return {"message": "Menu item not found"}, 404

        return jsonify({
            **menu.to_dict(),
            "owner_name": menu.owner.name if menu.owner else "Unknown"  # Add owner name
        })

    @jwt_required()  
    def patch(self, menu_id):
        menu = OwnerMenu.query.get(menu_id)
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

    @jwt_required()  
    def delete(self, menu_id):
        menu = OwnerMenu.query.get(menu_id)
        if not menu:
            return {"message": "Menu item not found"}, 404

        db.session.delete(menu)
        db.session.commit()

        MenuItem.query.filter_by(owner_menu_id=menu_id).delete()
        db.session.commit()

        return {"message": "Menu item deleted successfully"}, 200
   
api.add_resource(OwnerMenuResource, '/ownermenu')
api.add_resource(SingleOwnerMenuResource, '/ownermenu/<int:menu_id>')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
