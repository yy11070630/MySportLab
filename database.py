from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    _tablename_ = 'users'

    # =========================
    # BASIC INFO
    # =========================
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # =========================
    # PROFILE INFO
    # =========================
    avatar = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    height = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.String(10), nullable=True)
    fitness_level = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    # =========================
    # OPTIONAL 
    # =========================
    is_admin = db.Column(db.Boolean, default=False)

    def _repr_(self):
        return f'<User {self.username}>'