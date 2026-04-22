from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS                # Allow the frontend (on a different port) to call the backend API.
from datetime import datetime, timedelta   # Processing time (Token expiration time)
from database import db, User
import jwt                                 # Create and check tokens (used for login verification)
import os                                  # File handling (for avatar uploads)
import re                                  # Hashing passwords
from werkzeug.security import generate_password_hash, check_password_hash # Hashing passwords
               

# ================================================
# APP SETUP
# ================================================
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MY-SPORT-LAB-MINIITCSP1123'  # Secret key for JWT

db.init_app(app)    # Connect the database to your Flask application.
CORS(app)   # Allow the frontend to call the API


# ================================================
# Token Verification
# ================================================
def verify_token(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None, 'Token missing'

    try:
        token = auth_header.split(" ")[1]

        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(data['user_id'])

        if not user:
            return None, 'User not found'

        return user, None

    except Exception:
        return None, 'Invalid or expired token'
    

#================================================
# Registration API
#================================================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    confirm = data.get('confirm')
    email = data.get('email')


    # Username validation
    if not username:
        return jsonify({'success': False, 'message': 'Username is required'}), 400

    if " " in username:
        return jsonify({'success': False, 'message': 'Username cannot contain spaces'}), 400

    if len(username) > 30:
        return jsonify({'success': False, 'message': 'Username max 30 characters'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    

    # Email validation   
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    

    # Password validation
    if not password:
        return jsonify({'success': False, 'message': 'Password is required'}), 400

    if len(password) < 8 or len(password) > 12:
        return jsonify({'success': False, 'message': 'Password must be 8-12 characters'}), 400

    if not re.search(r"[A-Z]", password):
        return jsonify({'success': False, 'message': 'Must include uppercase letter'}), 400

    if not re.search(r"[a-z]", password):
        return jsonify({'success': False, 'message': 'Must include lowercase letter'}), 400

    if not re.search(r"[0-9]", password):
        return jsonify({'success': False, 'message': 'Must include a number'}), 400

    if not re.search(r"[^A-Za-z0-9]", password):
        return jsonify({'success': False, 'message': 'Must include a symbol'}), 400
    
    # Confirm password
    if password != confirm:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
    

    # Hash password
    hashed_password = generate_password_hash(password)
    

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
    
    if not check_password_hash(user.password, password):
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


# ================================================
# Upload folder
# ================================================
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================================
# Get Profile (Protected)
# ================================================
@app.route('/api/profile', methods=['GET'])
def get_profile():

    user, error = verify_token(request)

    if error:
        return jsonify({'success': False, 'message': error}), 401

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar,
            'gender': user.gender,
            'height': user.height,
            'weight': user.weight,
            'fitness_level': user.fitness_level,
            'country': user.country,
            'bio': user.bio,
            'date_of_birth': str(user.date_of_birth)
        }
    })


# ================================================
# Update Profile (Protected + Avatar upload)
# ================================================
@app.route('/api/profile', methods=['PUT'])
def update_profile():

    user, error = verify_token(request)

    if error:
        return jsonify({'success': False, 'message': error}), 401

    form = request.form

    user.gender = form.get('gender')
    user.height = form.get('height')
    user.weight = form.get('weight')
    user.fitness_level = form.get('fitness_level')
    user.country = form.get('country')
    user.bio = form.get('bio')

    dob = form.get('date_of_birth')
    if dob:
        user.date_of_birth = datetime.strptime(dob, "%Y-%m-%d")

    file = request.files.get('avatar')
    if file:
        filename = f"user_{user.id}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        user.avatar = f"/{filepath}"

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    })


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
    app.run(host='0.0.0.0', debug=True, port=5000)