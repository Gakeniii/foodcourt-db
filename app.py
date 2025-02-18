#!/usr/bin/env python3

import os

from flask import Flask, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from dotenv import load_dotenv
from sqlalchemy import MetaData

load_dotenv()

from models import db, User, OwnerMenu, Outlet, MenuItem, Order, OrderItem, TableBooking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

CORS(app,  resources={r"/api/*": {"origins": "*"}})

class Birds(Resource):

    def get(self):
        birds = [bird.to_dict() for bird in User.query.all()]
        return make_response(jsonify(birds), 200)

api.add_resource(Birds, '/birds')