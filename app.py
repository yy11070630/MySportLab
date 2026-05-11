from flask import Flask, request, render_template, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS                # Allow the frontend (on a different port) to call the backend API.
from datetime import datetime, timedelta   # Processing time (Token expiration time)
from database import db, User, UserProfile, Admin
from functools import wraps
import os                                  # File handling (for avatar uploads)
import re                                  # Hashing passwords
from werkzeug.security import generate_password_hash, check_password_hash # Hashing passwords
               
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LAWRENCE TAN YANG YI (252FC251VC)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ================================================
# APP SETUP
# ================================================
app = Flask(__name__, template_folder='frontend')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MY-SPORT-LAB-MINIITCSP1123'  # Secret key for JWT

db.init_app(app)    # Connect the database to your Flask application.
CORS(app, resources={r"/api/*": {"origins": "*"}})


#================================================
# Login Required Decorator (User & Admin)
#================================================
# User login 
def get_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper
    

# Admin login 
def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return wrapper

# =========================
# Home
# =========================
@app.route('/')
def home():
    user = get_user()

    if not user:
        return render_template('index.html', logged_in=False)

    profile = user.profile

    if not profile or not profile.has_completed_question:
        return render_template('index.html', logged_in=True, completed=False)


    return render_template('index.html', logged_in=True, completed=True)


#================================================
# Registration API
#================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

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

        session['user_id'] = new_user.id

        return redirect(url_for('question'))

    return render_template('register.html')


#================================================
# Login API
#================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        profile = user.profile

        if not profile or not profile.has_completed_question:
            return redirect(url_for('question'))
        else:
            return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        

        if not username or not password:
            return "Username and password required"
        
        # Search user
        user = User.query.filter_by(username=username).first()
        
        # Verify password
        if not user:
            return "Invalid username or password"
    
        if not check_password_hash(user.password, password):
            return "Invalid username or password"   
    
        session['user_id'] = user.id

        profile = user.profile

        if not profile or not profile.has_completed_question:
            return redirect(url_for('question'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# ================================================
# Logout API
# ================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ================================================
# Start route (check question status)
# ================================================
@app.route('/start')
def start():
    user = get_user()

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    profile = user.profile

    user = User.query.get(session['user_id'])

    if not user.profile or not user.profile.has_completed_question:
        return redirect(url_for('question'))

    return render_template('restart_question.html')


# ================================================
# Plan btn (check question status)
# ================================================
@app.route('/plan')
def plan():
    user = get_user()

    if not user:
        return redirect(url_for('login'))

    if not user.profile.has_completed_question:
        return redirect(url_for('question'))

    return render_template('plan.html')


# ================================================
# Chat btn (check question status)
# ================================================
@app.route('/chat')
def chat():
    user = get_user()

    if not user:
        return redirect(url_for('login'))

    if not user.profile.has_completed_question:
        return redirect(url_for('question'))

    return render_template('chat.html')


# ================================================
# Submit Question API
# ================================================
@app.route('/question', methods=['GET','POST'])
@login_required 
def question():
    user = User.query.get(session['user_id'])
    profile = user.profile

    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    if profile.has_completed_question:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        age_range = request.form.get('age_range')
        gender = request.form.get('gender')
        height = float(request.form.get('height'))
        weight = float(request.form.get('weight'))
        fitness = request.form.get('fitness_level')
        country = request.form.get('country')
        dob = request.form.get('dob')

        if not all([age_range, gender, height, weight, dob]):
            return "Please fill all required fields"
        
        height = float(height)
        weight = float(weight)

        # Count age from dob
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

        # Check age and age_range consistency
        if age < 18 and age_range != "0-17":
            return "Age does not match age range"

        if 18 <= age < 65 and age_range != "18-64":
            return "Age does not match age range"

        if age >= 65 and age_range != "65+":
            return "Age does not match age range"


        # Store in database
        profile.age_range = age_range
        profile.gender = gender
        profile.height = height
        profile.weight = weight
        profile.fitness_level = fitness
        profile.country = country
        profile.date_of_birth = birth_date

        profile.has_completed_question = True

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('question.html')


# ================================================
# Reset Questionnaire API
# ================================================
@app.route('/reset_questionnaire', methods=['POST'])
def reset_questionnaire():
    # check user login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # restart questionnaire
    if user.profile:
        user.profile.has_completed_question = False
        # clean questionnaire answers (if any)
        if hasattr(user.profile, 'questionnaire_answers'):
            user.profile.questionnaire_answers = None
        db.session.commit()
    
    # redirect to question page
    return redirect(url_for('question'))


# ================================================
# Dashboard 
# ================================================
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    profile = user.profile

    height = None
    weight = None
    bmi = None
    category = None
    
    if profile and profile.height and profile.weight:
        height = profile.height
        weight = profile.weight
        bmi = profile.weight / ((profile.height / 100) ** 2)

        if profile.age_range == "65+":
            if bmi < 18.5:
                category = "Underweight (Low)"
            elif bmi < 25:
                category = "Normal"
            else:
                category = "Overweight (High)"

        elif profile.age_range == "0-17":
            if profile.gender == "male":
                if bmi < 5:
                    category = "Underweight"
                elif bmi < 85:
                    category = "Normal"
                elif bmi < 95:
                    category = "Overweight"
                else:
                    category = "Obese"
            else:  
                if bmi < 5:
                    category = "Underweight"
                elif bmi < 85:
                    category = "Normal"
                elif bmi < 95:
                    category = "Overweight"
                else:
                    category = "Obese"

            category = category or "Child BMI (requires percentile table)"

        else:
            if bmi < 18.5:
                category = "Underweight"
            elif bmi < 23:
                category = "Normal"
            elif bmi < 27.5:
                category = "Overweight"
            else:
                category = "Obese"

    return render_template('dashboard.html', 
                           bmi=bmi, 
                           category=category,
                           height=profile.height,
                           weight=profile.weight)

# ================================================
# Upload folder 
# ================================================
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================================
# Update Profile (Protected + Avatar upload) 
# ================================================
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    profile = user.profile

    if request.method == 'POST':

        profile.bio = request.form.get('bio')

        file = request.files.get('avatar')
        if file:
            filename = f"user_{user.id}.png"
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)
            profile.avatar = filepath

        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', profile=profile, user=user)


# ================================================
# Admin Login API 
# ================================================
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(
            username=request.form.get('username')
        ).first()

        if not admin or not check_password_hash(admin.password, request.form.get('password')):
            return render_template('admin_login.html', error="Invalid admin login")

        session['admin_id'] = admin.id
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')


# ================================================
# Admin Dashboard 
# ================================================
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)


# ================================================
# Recommendation Sport API
# ================================================
@app.route('/recommendation', methods=['GET','POST'])
@login_required
def recommendation():
    if request.method == 'POST':
        physically = request.form.getlist('physically')
        activity_type = request.form.getlist('activity_type')
        daily_activity = request.form.get('daily_activity')
        goal = request.form.get('goal')

        # store in session (temporary, no DB needed)
        session['rec_input'] = {
            "physically": physically,
            "activity_type": activity_type,
            "daily_activity": daily_activity,
            "goal": goal
        }

        return redirect(url_for('recommendation_result'))

    return render_template('recommendation.html')


# ================================================
# Recommendation Result API
# ================================================
@app.route('/recommendation-result')
@login_required
def recommendation_result():
    data = session.get('rec_input')

    if not data:
        return redirect(url_for('recommendation'))

    physically = data['physically']
    activity_type = data['activity_type']
    daily = data['daily_activity']
    goal = data['goal']

    scores = {
        "Football": 0,
        "Basketball": 0,
        "Gym": 0,
        "Swimming": 0,
        "Badminton": 0,
        "Cycling": 0,
        "Running": 0
    }

    #=========================
    # Physically Ability
    #=========================
    if "Running fast" in physically:
        scores["Football"] += 2
        scores["Basketball"] += 2
        scores["Running"] += 2

    if "Long stamina" in physically:
        scores["Running"] += 2
        scores["Cycling"] += 2
        scores["Football"] += 1
        scores["Basketball"] += 1

    if "Strong upper body" in physically:
        scores["Gym"] += 3
        scores["Swimming"] += 2

    if "Flexible body" in physically:
        scores["Swimming"] += 2
        scores["Badminton"] += 2

    if "Good balance" in physically:
        scores["Cycling"] += 2
        scores["Badminton"] += 2

    if "Quick reflexes" in physically:
        scores["Basketball"] += 2
        scores["Football"] += 2
        scores["Badminton"] += 2

    #=========================
    # Activity Preference
    #=========================
    if "Team activities" in activity_type:
        scores["Football"] += 2
        scores["Basketball"] += 2

    if "Solo activities" in activity_type:
        scores["Gym"] += 2
        scores["Swimming"] += 2

    if "Indoor activities" in activity_type:
        scores["Gym"] += 1
        scores["Badminton"] += 1

    if "Outdoor activities" in activity_type:
        scores["Cycling"] += 2
        scores["Running"] += 2

    #=========================
    # Daily Activity Level
    #=========================
    if daily == "Very active":
        scores["Football"] += 2
        scores["Basketball"] += 2
        scores["Running"] += 2

    elif daily == "Moderately active":
        scores["Badminton"] += 2
        scores["Swimming"] += 2
        scores["Gym"] += 2

    elif daily == "Slightly active":
        scores["Gym"] += 2
        scores["Swimming"] += 1

    elif daily == "Rarely active":
        scores["Swimming"] += 2
        scores["Gym"] += 2

    #=========================
    # Goal
    #=========================
    if goal == "Lose weight":
        scores["Running"] += 2
        scores["Cycling"] += 2
        scores["Swimming"] += 2

    if goal == "Build muscle":
        scores["Gym"] += 3

    if goal == "Improve stamina":
        scores["Running"] += 3
        scores["Football"] += 2

    if goal == "Reduce stress":
        scores["Swimming"] += 2
        scores["Yoga"] = scores.get("Yoga", 0) + 3

    if goal == "Have fun & socialize":
        scores["Basketball"] += 2
        scores["Football"] += 2
        scores["Badminton"] += 2

    #=========================
    # Result Calculation
    #=========================
    best_sport = max(scores, key=scores.get)

    # match percentage
    max_score = scores[best_sport]
    percentage = min(100, max_score * 10)

    return render_template(
        "recommendation_result.html",
        sport=best_sport,
        percentage=percentage,
        scores=scores
    )


#================================================
# Start 
#================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Database created!')

        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                email='admin@gmail.com',
                password=generate_password_hash('admin123')
            )

            db.session.add(admin)
            db.session.commit()
            print("Admin created!")

    app.run(debug=True)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ALOYSIUS CHUAH MING YI (252FC2539X)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LIM SHAO QI (252FC2530B)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------