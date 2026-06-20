from unicodedata import category
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS                # Allow the frontend (on a different port) to call the backend API.
from datetime import datetime, timedelta, date  # Processing time (Token expiration time)
from database import db, User, UserProfile, Admin, Schedule, Food  # Import your database models
from functools import wraps
import os                                  # File handling (for avatar uploads)
import random                                
import re                                  # Hashing passwords
from werkzeug.security import generate_password_hash, check_password_hash # Hashing passwords
               

# ================================================
# APP SETUP (LAWRENCE)
# ================================================
app = Flask(__name__, template_folder='frontend')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MY-SPORT-LAB-MINIITCSP1123'  # Secret key for JWT

db.init_app(app)    # Connect the database to your Flask application.
CORS(app, resources={r"/api/*": {"origins": "*"}})


#================================================
# Login Required Decorator (User & Admin) (LAWRENCE)
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
# Home (LAWRENCE)
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
# Register (LAWRENCE)
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
            return render_template('register.html', error='Username is required')

        if " " in username:
            return render_template('register.html', error='Username cannot contain spaces')

        if len(username) > 30:
            return render_template('register.html', error='Username max 30 characters')

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
    

        # Email validation   
        if not email:
            return render_template('register.html', error='Email is required')

        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            return render_template('register.html', error='Invalid email format')

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
    

        # Password validation
        if not password:
            return render_template('register.html', error='Password is required')

        if len(password) < 8 or len(password) > 12:
            return render_template('register.html', error='Password must be 8-12 characters')

        if not re.search(r"[A-Z]", password):
            return render_template('register.html', error='Must include uppercase letter')

        if not re.search(r"[a-z]", password):
            return render_template('register.html', error='Must include lowercase letter')

        if not re.search(r"[0-9]", password):
            return render_template('register.html', error='Must include a number')

        if not re.search(r"[^A-Za-z0-9]", password):
            return render_template('register.html', error='Must include a symbol')
    
        # Confirm password
        if password != confirm:
            return render_template('register.html', error='Passwords do not match')


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
# Login (LAWRENCE)
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
            return render_template('login.html', error="Username and password required")

        
        # Search user
        user = User.query.filter_by(username=username).first()
        
        # Verify password
        if not user:
            return render_template('login.html', error="Invalid username or password")
    
        if not check_password_hash(user.password, password):
            return render_template('login.html', error="Invalid username or password")  
    
        session['user_id'] = user.id

        profile = user.profile

        if not profile or not profile.has_completed_question:
            return redirect(url_for('question'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# ================================================
# Forgot Password (LAWRENCE)
# ================================================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        user = User.query.filter_by(
            username=username,
            email=email
        ).first()

        if not user:
            return render_template(
                'forgot_password.html',
                error="Username or Email incorrect"
            )

        if password != confirm:
            return render_template(
                'forgot_password.html',
                error="Passwords do not match"
            )

        user.password = generate_password_hash(password)

        db.session.commit()

        return redirect(url_for('login'))

    return render_template('forgot_password.html')


# ================================================
# Logout (LAWRENCE)
# ================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ================================================
# Start route (check question status) (LAWRENCE)
# ================================================
@app.route('/start')
def start():

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    if not user:
        return redirect(url_for('login'))

    if not user.profile or not user.profile.has_completed_question:
        return redirect(url_for('question'))

    return render_template('restart_question.html')


# ================================================
# Chat btn (check question status) (LAWRENCE)
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
# Submit Question (LAWRENCE)
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
# Reset Questionn (LAWRENCE)
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
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    profile = user.profile

    height = None
    weight = None
    bmi = None
    category = None
    today_sport = "Not set"
    today_time = "Not set"

    today = str(date.today())

    last_date = session.get('calorie_date')

    if last_date != today:

        session['calorie_logs'] = []

        session['calorie_date'] = today

    calorie_logs = session.get('calorie_logs', [])

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

    schedule = session.get('schedule', [])
    if schedule:
     
        weekday = datetime.now().strftime('%A')
    
        today_plan = next((item for item in schedule if item.get('day') == weekday), None)
        if today_plan:
            today_sport = today_plan.get('sport', 'Rest Day')
            today_time = f"{today_plan.get('from', '--')} - {today_plan.get('to', '--')}"
        else:
            today_sport = "Rest Day"
            today_time = "No schedule"
    else:
  
        today_sport = "No plan generated"
        today_time = "Go to Planner →"

    return render_template(
        'dashboard.html',
        user=user,
        bmi=bmi,
        category=category,
        height=profile.height,
        weight=profile.weight,
        today_sport=today_sport,
        today_time=today_time,
        calorie_logs=calorie_logs,
        today=today,
        profile=profile
        )

# =========================================
# CALORIE TRACKER
# =========================================
@app.route('/calorie_tracker', methods=['GET', 'POST'])
@login_required
def calorie_tracker():

    user = User.query.get(session['user_id'])
    profile = user.profile

    height = None
    weight = None
    bmi = None
    category = None

    if profile and profile.height and profile.weight:

        height = profile.height
        weight = profile.weight

        bmi = weight / ((height / 100) ** 2)

        if bmi < 18.5:
            category = "Underweight"

        elif bmi < 23:
            category = "Normal"

        elif bmi < 27.5:
            category = "Overweight"

        else:
            category = "Obese"

    today = str(date.today())

    if session.get('calorie_date') != today:
        session['calorie_logs'] = []
        session['calorie_date'] = today

    calorie_logs = session.get('calorie_logs', [])

    if request.method == 'POST':

        food_name = request.form.get('food_name')

        quantity = int(
            request.form.get('quantity', 1)
        )

        food = Food.query.filter_by(
            food_name=food_name
        ).first()

        if food:

            total_food_calories = (
                food.calories * quantity
            )

            calorie_logs.append({

                'food': food.food_name,

                'quantity': quantity,

                'calories': total_food_calories

            })

            session['calorie_logs'] = calorie_logs

    total_calories = sum(
        item['calories']
        for item in calorie_logs
    )

    if category and "Underweight" in category:

        recommended_calories = 2500

    elif category == "Normal":

        recommended_calories = 2000

    elif category and "Overweight" in category:

        recommended_calories = 1800

    else:

        recommended_calories = 1600


    remaining_calories = (
        recommended_calories -
        total_calories
    )

    progress = (
        total_calories /
        recommended_calories
    ) * 100

    progress = min(progress, 100)

    if progress < 50:

        calorie_status = "You can eat more today."

    elif progress < 100:

        calorie_status = "You are within your daily target."

    else:

        calorie_status = "Daily calorie goal exceeded."

    foods = Food.query.order_by(
        Food.food_name
    ).all()

    return render_template(
    'calorie_tracker.html',

    user=user,
    profile=profile,
    calorie_logs=calorie_logs,
    total_calories=total_calories,
    recommended_calories=recommended_calories,
    remaining_calories=remaining_calories,
    progress=progress,
    calorie_status=calorie_status,
    foods=foods
)

@app.route('/delete_food/<int:index>')
@login_required
def delete_food(index):

    calorie_logs = session.get(
        'calorie_logs',
        []
    )

    if 0 <= index < len(calorie_logs):

        calorie_logs.pop(index)

        session['calorie_logs'] = calorie_logs

    return redirect(
        url_for('calorie_tracker')
    )

@app.route('/load_foods')
def load_foods():

    foods = [

        # Malay Food
        ("Nasi Lemak", 322),
        ("Nasi Goreng", 550),
        ("Nasi Kandar", 700),
        ("Nasi Kerabu", 500),
        ("Nasi Dagang", 520),
        ("Nasi Minyak", 480),
        ("Nasi Ayam Penyet", 650),
        ("Satay Chicken", 250),
        ("Satay Beef", 280),
        ("Rendang Chicken", 450),
        ("Rendang Beef", 500),
        ("Ayam Goreng", 350),
        ("Sambal Sotong", 300),
        ("Ikan Bakar", 280),
        ("Mee Rebus", 450),

        # Chinese Food
        ("Chicken Rice", 607),
        ("Duck Rice", 650),
        ("Roast Pork Rice", 700),
        ("Char Kuey Teow", 740),
        ("Hokkien Mee", 650),
        ("Wantan Mee", 500),
        ("Pan Mee", 550),
        ("Yong Tau Foo", 350),
        ("Fried Rice", 600),
        ("Sweet and Sour Chicken", 550),
        ("Dim Sum", 350),
        ("Fish Ball Noodles", 450),

        # Indian Food
        ("Roti Canai", 301),
        ("Roti Telur", 350),
        ("Roti Tissue", 450),
        ("Roti Planta", 420),
        ("Roti Bom", 550),
        ("Thosai", 250),
        ("Capati", 180),
        ("Mee Goreng Mamak", 600),
        ("Maggi Goreng", 650),
        ("Tandoori Chicken", 400),

        # Noodles
        ("Mee Goreng", 520),
        ("Laksa", 432),
        ("Curry Mee", 500),
        ("Mee Bandung", 550),
        ("Mee Kari", 580),
        ("Bee Hoon Soup", 350),
        ("Fried Bee Hoon", 500),
        ("Kuey Teow Soup", 400),

        # Drinks
        ("Teh Tarik", 120),
        ("Teh O", 60),
        ("Kopi O", 50),
        ("Kopi", 90),
        ("Milo", 180),
        ("Bandung", 160),
        ("Lemon Tea", 70),
        ("Barley Drink", 90),
        ("Soy Milk", 130),
        ("100 Plus", 80),

        # Fruits
        ("Apple", 95),
        ("Banana", 105),
        ("Orange", 62),
        ("Watermelon", 46),
        ("Papaya", 60),
        ("Mango", 99),
        ("Guava", 68),
        ("Dragon Fruit", 60),
        ("Pineapple", 82),
        ("Durian", 357),

        # Fast Food
        ("Burger", 354),
        ("Cheeseburger", 400),
        ("French Fries", 365),
        ("Fried Chicken", 390),
        ("Pizza Slice", 285),
        ("Hot Dog", 290),
        ("Chicken Nugget", 270),

        # Desserts
        ("Cendol", 250),
        ("ABC", 300),
        ("Ais Kacang", 280),
        ("Kuih Lapis", 120),
        ("Onde Onde", 90),
        ("Kuih Seri Muka", 180)

    ]

    for name, kcal in foods:

        if not Food.query.filter_by(
            food_name=name
        ).first():

            db.session.add(
                Food(
                    food_name=name,
                    calories=kcal
                )
            )

    db.session.commit()

    return "Foods Loaded"




# ================================================
# Upload folder (LAWRENCE)
# ================================================
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================================
# Update Profile (Avatar upload) (LAWRENCE)
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
# Admin Login (LAWRENCE)    
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
# Admin Dashboard (LAWRENCE)
# ================================================
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)


# ================================================
# Recommendation Sport (LAWRENCE)
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
# Recommendation Result (LAWRENCE)
# ================================================
@app.route('/recommendation_result')
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
        scores["Running"] += 5
        scores["Football"] += 4
        scores["Basketball"] += 4  
        scores["Badminton"] += 3   

    if "Long stamina" in physically:
        scores["Running"] += 3
        scores["Football"] += 3
        scores["Swimming"] += 3
        scores["Cycling"] += 3
        scores["Basketball"] += 2
        scores["Badminton"] += 2
        scores["Gym"] += 1

    if "Strong upper body" in physically:
        scores["Gym"] += 5
        scores["Swimming"] += 4
        scores["Badminton"] += 3
        scores["Basketball"] += 2
        scores["Football"] += 1

    if "Flexible body" in physically:
        scores["Swimming"] += 5
        scores["Badminton"] += 4
        scores["Basketball"] += 3
        scores["Gym"] += 2  
        scores["Football"] += 2

    if "Good balance" in physically:
        scores["Cycling"] += 5
        scores["Badminton"] += 4
        scores["Basketball"] += 3
        scores["Football"] += 2
        scores["Running"] += 2
        scores["Swimming"] += 2
        scores["Gym"] += 1  

    if "Quick reflexes" in physically:
        scores["Badminton"] += 5
        scores["Basketball"] += 5
        scores["Football"] += 4 
        scores["Gym"] += 1       

    #=========================
    # Activity Preference 
    #=========================
    if "Team activities" in activity_type:
        scores["Football"] += 3
        scores["Basketball"] += 3
        scores["Badminton"] += 2  

    if "Solo activities" in activity_type:
        scores["Gym"] += 3
        scores["Swimming"] += 3
        scores["Running"] += 2
        scores["Cycling"] += 2

    if "Indoor activities" in activity_type:
        scores["Gym"] += 2
        scores["Badminton"] += 2
        scores["Swimming"] += 1 

    if "Outdoor activities" in activity_type:
        scores["Cycling"] += 3
        scores["Running"] += 3
        scores["Football"] += 2
        scores["Basketball"] += 2

    #=========================
    # Daily Activity Level 
    #=========================
    if daily == "Very active":
        scores["Running"] += 3
        scores["Football"] += 3
        scores["Basketball"] += 3
        scores["Badminton"] += 2
        scores["Swimming"] += 2

    elif daily == "Moderately active":
        scores["Badminton"] += 3
        scores["Swimming"] += 3
        scores["Gym"] += 3
        scores["Cycling"] += 2
        scores["Football"] += 1

    elif daily == "Slightly active":
        scores["Gym"] += 3
        scores["Swimming"] += 3
        scores["Cycling"] += 2
        scores["Badminton"] += 1

    elif daily == "Rarely active":
        scores["Swimming"] += 4  
        scores["Gym"] += 3       
        scores["Cycling"] += 2   
        scores["Running"] += 1   

    #=========================
    # Goal 
    #=========================
    if goal == "Lose weight":
        scores["Running"] += 4
        scores["Cycling"] += 3
        scores["Swimming"] += 3
        scores["Football"] += 2
        scores["Basketball"] += 2

    if goal == "Build muscle":
        scores["Gym"] += 5
        scores["Swimming"] += 2
        scores["Football"] += 1

    if goal == "Improve stamina":
        scores["Running"] += 4
        scores["Swimming"] += 3
        scores["Cycling"] += 3
        scores["Football"] += 2
        scores["Basketball"] += 2

    if goal == "Reduce stress":
        scores["Swimming"] += 4
        scores["Cycling"] += 3
        scores["Running"] += 2
        scores["Gym"] += 2

    if goal == "Have fun & socialize":
        scores["Basketball"] += 4
        scores["Football"] += 4
        scores["Badminton"] += 4
        scores["Swimming"] += 2

    #=========================
    # Result Calculation
    #=========================
    best_sport = max(scores, key=scores.get)

    max_score = scores[best_sport]

    # normalize against best possible score in system
    max_possible = max(scores.values())

    if max_possible == 0:
        percentage = 0
    else:
        percentage = int((max_score / max_possible) * 100)

    videos = {
        "Football": "https://www.youtube.com/embed/XJIqk0hQY3Y",
        "Basketball": "https://www.youtube.com/embed/wQk1qZ8Qy9s",
        "Gym": "https://www.youtube.com/embed/U0bhE67HuDY",
        "Swimming": "https://www.youtube.com/embed/6Jv0KXQ1x4A",
        "Badminton": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "Cycling": "https://www.youtube.com/embed/2eZ9XQ0mQ0k",
        "Running": "https://www.youtube.com/embed/5Q4K8r9xQ2A"
    }

    return render_template(
        "recommendation_result.html",
        sport=best_sport,
        percentage=percentage,
        scores=scores,
        video = videos.get(best_sport, "https://www.youtube.com")
    )

# ================================================
# Tutorial (LAWRENCE)
# ================================================
@app.route('/tutorial')
@login_required
def tutorial():

    tutorials = {

        "Football": [
            "3z0uB0rVg7M",
            "M1S0v8QGJ6I",
            "0Uqf71muwWc",
            "YJbV5Q6K5sA",
            "t6h2tK4fQ7o",
            "XJIqk0hQY3Y"
        ],

        "Basketball": [
            "LAr6oAKieHk",
            "wPDxUzJ8Jzw",
            "oyjYgmsM00Q",
            "rWOaROd9v7A",
            "x6a4hMyiwBo"
        ],

        "Gym": [
            "U0bhE67HuDY",
            "ml6cT4AZdqI",
            "2pLT-olgUJs",
            "gC_L9qAHVJ8",
            "ixkQaZXVQjs"
        ],

        "Swimming": [
            "6Jv0KXQ1x4A",
            "SX2N7gWmL6E",
            "I5GaxSYLCSc",
            "jQ4L9M8Y7s0"
        ],

        "Badminton": [
            "pf8R8T0Xk3g",
            "iD9Jq1K8G4Y",
            "8Wb8L5Y8x8g",
            "x6nEPn9YQ8Q"
        ],

        "Cycling": [
            "2eZ9XQ0mQ0k",
            "U3xK1z0J8vM",
            "Q4w2R8M9Y0s"
        ],

        "Running": [
            "5Q4K8r9xQ2A",
            "brFHyOtTwH4",
            "sTANio_2E0Q",
            "g_tea8ZNk5A"
        ]
    }

    return render_template("tutorial.html", tutorials=tutorials)

#================================================
# Plan (check question status + generate schedule) (Aloysius)
#================================================
@app.route('/plan', methods=['GET','POST'])
@login_required
def plan():
    
    user = User.query.get(session['user_id'])

    # Get fitness level from questionnaire profile
    fitness = user.profile.fitness_level
    
    if not user:
        return redirect(url_for('login'))
    
    # Check questionnaire completed
    if not user.profile.has_completed_question:
        return redirect(url_for('question'))
    
    # =========================================
    # POST
    # =========================================
    if request.method == 'POST':

        
        sports = request.form.getlist('sports')
        days = request.form.getlist('days')
        if not sports:
            return render_template(
            'plan.html',
            user=user,
            error="Please select at least one sport"
        )

        if not days:
            return render_template(
            'plan.html',
            user=user,
            error="Please select at least one day"
        )

        schedule = []

        #==================================
        # Duration based on fitness level
        #==================================
        if fitness == "Beginner":

            duration = "30-45 mins"
            intensity = "Light"

        elif fitness == "Intermediate":

            duration = "45-60 mins"
            intensity = "Medium"

        else:

            duration = "60-90 mins"
            intensity = "High"

        #==================================
        # Generate Schedule
        #==================================
        for day in days:

            starts = request.form.getlist(f"{day.lower()}_from")
            ends = request.form.getlist(f"{day.lower()}_to")

            for i in range(len(starts)):
                for j in range(i + 1, len(starts)):

                 if starts[i] == starts[j] and ends[i] == ends[j]:
                     return render_template(
                    'plan.html',
                    user=user,
                    error=f"{day}: Slot times cannot be the same"
            )
                 
            # End time must be later than start time
            for start, end in zip(starts, ends):

                 # Skip empty slots
                if not start or not end:
                    continue

                start_time = datetime.strptime(start, "%H:%M")
                end_time = datetime.strptime(end, "%H:%M")

                if end_time <= start_time:
                    return render_template(
                    'plan.html',
                    user=user,
                    error=f"{day}: End time must be later than start time"
            )
                
                # Maximum 6 hours per slot
                if end_time > start_time + timedelta(hours=6):
                    return render_template(
                        'plan.html',
                        user=user,
                        error=f"{day}: Each slot cannot exceed 6 hours"
    )
           

                # Validate time slot for at least 30 min duration
                if end_time < start_time + timedelta(minutes=30):
                    return render_template(
                        'plan.html',
                        user=user,
                        error=f"{day}: End time must be at least 30 minutes after start time"
                    )

                # Randomly select a sport
                sport = random.choice(sports)

                schedule.append({
                    "day": day,
                    "sport": sport,
                    "duration": duration,
                    "intensity": intensity,
                    "from": start,
                    "to": end
                })

                new_schedule = Schedule(
                    user_id=user.id,
                    day=day,
                    sport=sport,
                    duration=duration,
                    intensity=intensity,
                    start_time=start,
                    end_time=end
                )

                db.session.add(new_schedule)
                #end of all loops
                db.session.commit()

        # ==================================
        # Save into session
        # ==================================
        session['schedule'] = schedule

        saved_schedule = Schedule.query.filter_by(
        user_id=user.id
        ).all()

        return render_template(
            'plan.html',
            user=user,
            schedule=saved_schedule
        )
        
    # =========================================
    # GET existing schedule
    # =========================================
    saved_schedule = Schedule.query.filter_by(
    user_id=user.id
    ).all()

    return render_template(
        'plan.html',
        user=user,
        schedule=saved_schedule,
        error=None
    )

# =========================================
# Edit Schedule (Aloysius)
# =========================================
@app.route('/edit_schedule/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(id):

    schedule = Schedule.query.get_or_404(id)

    if request.method == 'POST':

        start_time = datetime.strptime(
            request.form['start_time'],
            "%H:%M"
        )

        end_time = datetime.strptime(
            request.form['end_time'],
            "%H:%M"
        )

        if end_time <= start_time:
            return render_template(
                'edit_schedule.html',
                schedule=schedule,
                error="End time must be later than start time"
            )

        schedule.start_time = request.form['start_time']
        schedule.end_time = request.form['end_time']
        schedule.sport = request.form['sport']

        db.session.commit()

        return redirect('/plan')
    
    return render_template(
        'edit_schedule.html',
        schedule=schedule
    )
#========================================
# delete schedule (Aloysius)
#========================================
@app.route('/delete_schedule/<int:id>', methods=['POST'])
@login_required
def delete_schedule(id):

    schedule = Schedule.query.get_or_404(id)

    db.session.delete(schedule)
    db.session.commit()

    return redirect('/plan')

@app.route('/delete_all_schedule', methods=['POST'])
@login_required
def delete_all_schedule():

    Schedule.query.filter_by(
        user_id=session['user_id']
    ).delete()

    db.session.commit()

    return redirect('/plan')
#================================================
# Start (LAWRENCE)
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



