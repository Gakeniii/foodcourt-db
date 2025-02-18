#!/usr/bin/env python3

import os

from flask import Flask, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv

load_dotenv()

from models import db, User, OwnerMenu, Outlet, MenuItem, Order, OrderItem, TableBooking


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Birds(Resource):

    def get(self):
        birds = [bird.to_dict() for bird in User.query.all()]
        return make_response(jsonify(birds), 200)

api.add_resource(Birds, '/birds')