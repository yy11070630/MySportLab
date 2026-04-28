from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS                # Allow the frontend (on a different port) to call the backend API.
from datetime import datetime, timedelta   # Processing time (Token expiration time)
from database import db, User, UserProfile, Admin
import jwt                                 # Create and check tokens (used for login verification)
import json
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
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 200


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
    db.session.flush()  
    
    new_profile = UserProfile(user_id=new_user.id)
    db.session.add(new_profile)
    
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
# Check user status (questionnaire) API
# ================================================
@app.route('/api/user/status', methods=['GET'])
def get_user_status():
    user, error = verify_token(request)
    if error:
        return jsonify({'success': False, 'message': error}), 401
    
    # Check user has completed questionnaire
    # Note: you need to add this field to the UserProfile 
    has_completed = False
    age_rannge = None

    if user.profile:
        has_completed = user.profile.has_completed_questionnaire if hasattr(user.profile, 'has_completed_questionnaire') else False

        if hasattr(user.profile, 'questionnaire_answers') and user.profile.questionnaire_answers:
            try:
                answers = json.loads(user.profile.questionnaire_answers) if isinstance(user.profile.questionnaire_answers, str) else user.profile.questionnaire_answers
                age_range = answers.get('age_range') if answers else None
            except:
                pass
    
    return jsonify({
        'success': True,
        'has_completed_questionnaire': has_completed,
        'age_range': age_range
    }), 200


# ================================================
# Submit Questionnaire API
# ================================================
@app.route('/api/questionnaire', methods=['POST'])
def submit_questionnaire():
    user, error = verify_token(request)
    if error:
        return jsonify({'success': False, 'message': error}), 401
    
    data = request.get_json()
    answers = data.get('answers')
    
    # Create or update the user's profile
    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
    
    # Mark the user as having completed the questionnaire
    profile.has_completed_questionnaire = True
    
    profile.questionnaire_answers = json.dumps(answers) if answers else '{}'

    # Save questionnaire answers to the corresponding fields in the profile
    if answers:
        if answers.get('gender'):
            profile.gender = answers.get('gender')
        if answers.get('height'):
            profile.height = float(answers.get('height')) if answers.get('height') else None
        if answers.get('weight'):
            profile.weight = float(answers.get('weight')) if answers.get('weight') else None
        if answers.get('fitness_level'):
            profile.fitness_level = answers.get('fitness_level')
        if answers.get('country'):
            profile.country = answers.get('country')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Questionnaire submitted successfully'
    }), 200


# ================================================
# Get Questionnaire Answers (for preview)
# ================================================
@app.route('/api/questionnaire', methods=['GET'])
def get_questionnaire():
    user, error = verify_token(request)
    if error:
        return jsonify({'success': False, 'message': error}), 401
    
    profile = user.profile
    answers = None
    has_submitted = False
    
    if profile:
        has_submitted = profile.has_completed_questionnaire if hasattr(profile, 'has_completed_questionnaire') else False
        if hasattr(profile, 'questionnaire_answers') and profile.questionnaire_answers:
            answers = profile.questionnaire_answers
    
    return jsonify({
        'success': True,
        'has_submitted': has_submitted,
        'answers': answers
    }), 200


# ================================================
# Get User Info (for Dashboard)
# ================================================
@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    user, error = verify_token(request)
    if error:
        return jsonify({'success': False, 'message': error}), 401
    
    profile = user.profile
    
    # Get age range from questionnaire answers
    age_range = None
    if profile and hasattr(profile, 'questionnaire_answers') and profile.questionnaire_answers:
        try:
            import json
            answers = json.loads(profile.questionnaire_answers) if isinstance(profile.questionnaire_answers, str) else profile.questionnaire_answers
            age_range = answers.get('age_range') if answers else None
        except:
            pass
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'profile': {
            'avatar': profile.avatar if profile else None,
            'gender': profile.gender if profile else None,
            'height': profile.height if profile else None,
            'weight': profile.weight if profile else None,
            'fitness_level': profile.fitness_level if profile else None,
            'country': profile.country if profile else None,
            'bio': profile.bio if profile else None,
            'date_of_birth': str(profile.date_of_birth) if profile and profile.date_of_birth else None,
            'has_completed_questionnaire': profile.has_completed_questionnaire if profile else False,
            'age_range': age_range  
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
    
    profile = user.profile  
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'profile': {
            'avatar': profile.avatar if profile else None,
            'gender': profile.gender if profile else None,
            'height': profile.height if profile else None,
            'weight': profile.weight if profile else None,
            'fitness_level': profile.fitness_level if profile else None,
            'country': profile.country if profile else None,
            'bio': profile.bio if profile else None,
            'date_of_birth': str(profile.date_of_birth) if profile and profile.date_of_birth else None,
            'has_completed_questionnaire': profile.has_completed_questionnaire if profile else False
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
    
    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
    
    form = request.form
    
    profile.gender = form.get('gender')
    profile.height = form.get('height')
    profile.weight = form.get('weight')
    profile.fitness_level = form.get('fitness_level')
    profile.country = form.get('country')
    profile.bio = form.get('bio')
    
    dob = form.get('date_of_birth')
    if dob:
        from datetime import datetime
        profile.date_of_birth = datetime.strptime(dob, "%Y-%m-%d")
    
    file = request.files.get('avatar')
    if file:
        import os
        filename = f"user_{user.id}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        profile.avatar = f"/{filepath}"
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})


# ================================================
# Admin Token Verification
# ================================================
def verify_admin_token(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None, 'Token missing'

    try:
        token = auth_header.split(" ")[1]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        
        # Check if the user is an admin
        if data.get('role') != 'admin':
            return None, 'Admin access required'
        
        admin = Admin.query.get(data.get('admin_id'))
        if not admin:
            return None, 'Admin not found'

        return admin, None

    except Exception:
        return None, 'Invalid or expired token'
    

# ================================================
# Admin Login API
# ================================================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Find admin
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin:
        return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 401
    
    if not check_password_hash(admin.password, password):
        return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 401
    
    # Create Token（have role info in token to distinguish from user token）
    token = jwt.encode({
        'admin_id': admin.id,
        'role': 'admin',
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Admin login successful',
        'token': token,
        'admin': {
            'id': admin.id,
            'username': admin.username,
            'email': admin.email
        }
    }), 200


# ================================================
# Admin - Get All Users
# ================================================
@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    admin, error = verify_admin_token(request)
    
    if error:
        return jsonify({'success': False, 'message': error}), 401
    
    # Get all regular users
    users = User.query.all()
    
    return jsonify({
        'success': True,
        'users': [user.to_dict() for user in users]
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
    app.run(host='0.0.0.0', debug=True, port=5000)