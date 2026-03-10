#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# 1. GET /heroes
class Heroes(Resource):
    def get(self):
        heroes = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in Hero.query.all()]
        return make_response(heroes, 200)

# 2. GET /heroes/:id
class HeroByID(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if hero:
            return make_response(hero.to_dict(), 200)
        return make_response({"error": "Hero not found"}, 404)

# 3. GET /powers & GET /powers/:id & PATCH /powers/:id
class Powers(Resource):
    def get(self):
        powers = [power.to_dict(only=('description', 'id', 'name')) for power in Power.query.all()]
        return make_response(powers, 200)

class PowerByID(Resource):
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if power:
            return make_response(power.to_dict(only=('description', 'id', 'name')), 200)
        return make_response({"error": "Power not found"}, 404)

    def patch(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return make_response({"error": "Power not found"}, 404)
        
        try:
            data = request.get_json()
            for attr in data:
                setattr(power, attr, data.get(attr))
            db.session.commit()
            return make_response(power.to_dict(only=('description', 'id', 'name')), 200)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

# 4. POST /hero_powers
class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_hero_power = HeroPower(
                strength=data.get('strength'),
                hero_id=data.get('hero_id'),
                power_id=data.get('power_id')
            )
            db.session.add(new_hero_power)
            db.session.commit()
            # Return full dict including nested hero and power data
            return make_response(new_hero_power.to_dict(), 200)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

# Add Resources to API
api.add_resource(Heroes, '/heroes')
api.add_resource(HeroByID, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerByID, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
