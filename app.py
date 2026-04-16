from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS                # Allow the frontend (on a different port) to call the backend API.
from datetime import datetime, timedelta   # Processing time (Token expiration time)
import jwt                                 # Create and check tokens (used for login verification)
import hashlib                             # Hashing passwords

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MY-SPORT-LAB-MINIITCSP1123'  # Secret key for JWT

db = SQLAlchemy(app)
CORS(app)   # Allow the frontend to call the API


#================================================
# User table
#================================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


#================================================
# Registration API
#================================================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Check if username and password are provided
    if not username or not password:    
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():  
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    # Check if the email already exists (if provided)
    if email and User.query.filter_by(email=email).first():  
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  

    # Create user
    new_user = User(username=username, password=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    # Generate Token
    token = jwt.encode({
        'user_id': new_user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'token': token,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201


#================================================
# Login API
#================================================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Search user
    user = User.query.filter_by(username=username).first()
    
    # Verify password
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user.password != hashed_password:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200


#================================================
# Test route
#================================================
@app.route('/')
def index():
    return 'MySportLab API is running!'


#================================================
# Start
#================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Database created!')
    app.run(debug=True)