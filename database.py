from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =========================
# User Table (ALOYSIUS)
# =========================
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # One-to-One relationship with profile
    profile = db.relationship('UserProfile', backref='user', uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"

# =========================
# User Profile Table (ALOYSIUS)
# =========================
class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Basic info
    age_range = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)     # cm
    weight = db.Column(db.Float)     # kg
    fitness_level = db.Column(db.String(50))
    country = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)


    # Extra profile
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200))

    # Questionnaire status
    has_completed_question = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Profile user_id={self.user_id}>"

# =========================
# Food Table (SHAO QI)
# =========================
class Food(db.Model):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    calories = db.Column(
        db.Float,
        nullable=False
    )

    def __repr__(self):
        return f"<Food {self.food_name}>"

# =========================
# Calorie Log Table (SHAO QI)
# =========================
class CalorieLog(db.Model):
    __tablename__ = 'calorie_log'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    food_name = db.Column(
        db.String(100),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    calories = db.Column(
        db.Float,
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow().date
    )

    def __repr__(self):
        return f"<CalorieLog {self.food_name}>"

# =========================
# Admin Table (ALOYSIUS)
# =========================
class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120))
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"

#=========================
# #Schedule Table (Aloysius)
#=========================   
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    day = db.Column(db.String(20))
    sport = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    intensity = db.Column(db.String(50))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))