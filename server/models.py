from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # Relationship: A Hero has many HeroPowers
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')
    
    # Serialization: Exclude hero_powers from the nested hero object to avoid recursion
    serialize_rules = ('-hero_powers.hero',)

    def __repr__(self):
        return f'<Hero {self.id}: {self.super_name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # Relationship: A Power has many HeroPowers
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    
    # Serialization: Avoid recursion back to hero_powers
    serialize_rules = ('-hero_powers.power',)

    # Validation: description must be present and at least 20 characters long
    @validates('description')
    def validate_description(self, key, description):
        if not description or len(description) < 20:
            raise ValueError("Description must be present and at least 20 characters long.")
        return description

    def __repr__(self):
        return f'<Power {self.id}: {self.name}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    # Foreign Keys
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Relationships
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # Serialization: Exclude hero and power from the nested hero_power object to avoid recursion
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers',)

    # Validation: strength must be one of 'Strong', 'Weak', 'Average'
    @validates('strength')
    def validate_strength(self, key, strength):
        allowed = ['Strong', 'Weak', 'Average']
        if strength not in allowed:
            raise ValueError("Strength must be one of: 'Strong', 'Weak', 'Average'.")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}: Hero {self.hero_id} - Power {self.power_id}>'