import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)

    def set_password(self, password):
        """Set the user's password (hashed)."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.email

    def dict(self):
        """Return a dictionary representation of the User."""
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email,
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gravity = Column(Integer, nullable=False)
    terrain = Column(String(250), nullable=False)
    climate = Column(String(250), nullable=False)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def dict(self):
        """Return a dictionary representation of the Planet."""
        return {
            "id": self.id,
            "name": self.name,
            "gravity": self.gravity,
            "terrain": self.terrain,
            "climate": self.climate
        }

class People(db.Model):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    height = Column(Float, nullable=False)
    eye_color = Column(String(250))
    mass = Column(Integer, nullable=False)

    def __repr__(self):
        return '<People %r>' % self.id

    def dict(self):
        """Return a dictionary representation of the People."""
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "eye_color": self.eye_color,
            "mass": self.mass
        }

class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    id_planet = Column(Integer, ForeignKey(Planet.id), nullable=True, index=True)
    id_user = Column(Integer, ForeignKey(User.id), nullable=False, index=True)
    id_people = Column(Integer, ForeignKey(People.id), nullable=True, index=True)

    # Relationships
    planet = db.relationship('Planet', backref='favorites', lazy=True)
    user = db.relationship('User', backref='favorites', lazy=True)
    people = db.relationship('People', backref='favorites', lazy=True)

    def __repr__(self):
        return '<Favorites %r>' % self.id

    def dict(self):
        """Return a dictionary representation of the Favorites."""
        return {
            "id": self.id,
            "id_user": self.id_user,
            "user_name": self.user.name if self.user else None,
            "planet_name": self.planet.name if self.planet else None,
            "people_name": self.people.name if self.people else None
        }
