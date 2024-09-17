from flask_app import app
from flask import jsonify, logging, render_template, redirect, session, request, flash
from flask_app.models.user import User
from flask_app.models.blogs import Blog
from flask_app.models.diagnosis import Diagnosis
from flask_app.models.logs import Log
from flask_bcrypt import Bcrypt
from datetime import datetime, time
import datetime
from flask_app.config.mysqlconnection import connectToMySQL
import requests
import time

from flask_mail import Mail, Message
from random import randint
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler

 


load_dotenv()
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)
scheduler = BackgroundScheduler()

 

def verify_email(api_key, email):#Funksioni per verifikimin e emailit nepermjet API te EmailListVerify
    url = f'https://apps.emaillistverify.com/api/verifyEmail?secret={api_key}&email={email}'
    response = requests.get(url) #Therrasim API-n me metoden GET
    return response.text #Kthejme pergjigjen e API-s
  


bcrypt = Bcrypt(app)

@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')

import os   
from datetime import datetime
from werkzeug.utils import secure_filename
 


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = 'flask_app/static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/profilepic/user', methods=['POST'])
def new_profil_pic_user():
    if 'user_id' not in session:
        return redirect('/loginpage')
    data = {"id": session['user_id']}
    
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['image'] = filename
            User.update_profile_pic_user(data)
    
    return redirect('/profile')

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin':
            user_count = User.number_of_users()
            monthly_average=User.monthly_average_of_journals_per_user()
            active_users=User.active_users()
            low_mood_users=User.low_mood_users()

            return render_template('indexadminn.html', user_count=user_count, monthly_average=monthly_average, active_users=active_users, low_mood_users=low_mood_users)
        return redirect('/dashboard')
    return redirect('/homepage')

@app.route('/homepage')
def homepage():
    if 'user_id' in session:
        return redirect('/dashboard')
    blogs = Blog.get_all_blogposts()
    return render_template('index.html',blogs = blogs)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    loggedUser = User.get_user_by_id(data)
    blogs = Blog.get_all_blogposts()
    latest_diagnosis = Diagnosis.get_latest_diagnosis(data)
    return render_template('indexhome.html',loggedUser = loggedUser,questions =User.get_questions(),blogs = blogs,latest_diagnosis = latest_diagnosis)



@app.route('/register', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/')
    
    #Gjeneroj nje kod verifikimi me 6 shifra unik
    verification_code = randint(100000, 999999)  
    
    # Ruaj te dhenat e perdoruesit ne session perkohesisht derisa te verifikohet emaili
    session['user_data'] = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'confirm_password': bcrypt.generate_password_hash(request.form['confirm_password']),
        'age': request.form['age'],
        'role': 'user',
        'verification_code': verification_code, 
     }
    
    # Therras funksionin verify_email  per te verifikuar emailin nepermjet API te EmailListVerify
    api_key = os.getenv('API_KEY') # API key e EmailListVerify i ruajtur ne file .env
    email = request.form['email']# Emaili i perdoruesit qe do te verifikohet
    result = verify_email(api_key, email)# Rezultati i verifikimit

    if result == "ok":
        send_verification_email(email, verification_code)      # Dergojme emailin me kodin verifikues
        return redirect('/verify')# Nese emaili eshte valid, shkojme ne faqen verify.html per te verifikuar emailin
    flash('Emaili juaj nuk eshte valid. Na vjen keq!', 'emailSignUp')# Nese emaili nuk eshte valid, shfaqim nje mesazh gabimi
    return redirect(request.referrer)# Kthehemi ne faqen e regjistrimit


def send_verification_email(email, code):
    msg = Message('Email Verification Code', recipients=[email])
    msg.body = f'Your verification code is: {code}'
    mail.send(msg)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_data = session.get('user_data')
        if user_data:
            entered_code = request.form['verification_code']          
            if user_data['verification_code'] == int(entered_code):
                user_id = User.create_user(user_data)               
                session.pop('user_data', None)               
                session['user_id'] = user_id
                session['role'] = 'user'               
                return redirect('/')
            else:
                flash('Kodi i verifikimit nuk eshte i sakte ju lutem provojeni perseri!', 'error') 
    return render_template('verify.html')






@app.route('/login', methods=['POST'])
def login():
    if 'user_id' in session:
        return redirect('/')
    user = User.get_user_by_email(request.form)
    if not user:
        flash('This email does not exist.', 'email')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Your password is wrong!', 'password')
        return redirect(request.referrer)
    session['user_id'] = user['id']
    session['role'] = user['role']
    new_log_data = {
    'id': user['id'],
    'log': 'Successful login',
    'created_at': datetime.now()
    }
    Log.create_log(new_log_data)
    return redirect('/')


@app.route('/loginpage')
def loginpage():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return render_template('indexadminn.html')
        else:
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    # new_log_data = {
    # 'id': session['user_id'],
    # 'log': 'Successful logout',
    # 'created_at': datetime.now()
    # }
    # Log.create_log(new_log_data)
    return redirect('/')

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return ''
  
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/')
    
    data = {
        'id': session['user_id']
    }
    
    loggedUser = User.get_user_by_id(data)
    latest_diagnosis = Diagnosis.get_latest_diagnosis(data)
     
    return render_template('profile.html', loggedUser=loggedUser, latest_diagnosis=latest_diagnosis )

@app.route('/editprofile', methods=['POST'])
def editprofile():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'age': request.form['age']
    }
    User.update_user(data)
    new_log_data = {
    'id':  session['user_id'],
    'log': 'Successful profile update',
    'created_at': datetime.now()
    }
    Log.create_log(new_log_data)
    return redirect (request.referrer)



@app.route('/questionnaire', methods=['POST'])
def questionnaire():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = key.split('_')[1]
            answer = value
            data = {
                'user_id': user_id,
                'question_id': question_id,
                'answer': answer
            }
            User.add_answer(data)
    total_score = 0
    user_answers = User.get_answers_by_user_id({'user_id': user_id})
    total_score = sum(answer['answer'] for answer in user_answers)
    diagnosis = {}
    if total_score == 0:
        diagnosis['Status'] = 'No significant mental health concerns detected.'
    elif total_score <= 20:
        diagnosis['Overall Assessment'] = 'Low level of mental health concerns detected. Monitor the situation and seek help if things worsen.'
    elif 20 < total_score <= 40:
        diagnosis['Overall Assessment'] = 'Mild level of mental health concerns detected. Some intervention or support might be beneficial.'
    elif 40 < total_score <= 60:
        diagnosis['Overall Assessment'] = 'Moderate level of mental health concerns detected. Consultation with a mental health professional is recommended.'
    else:
        diagnosis['Overall Assessment'] = 'High level of mental health concerns detected. Immediate professional help is advised.'


    diagnosis_str = '\n'.join(f"{k}: {v}" for k, v in diagnosis.items())
    data = {'user_id': user_id, 'diagnosis': diagnosis_str}
    User.update_diagnosis(data)
    new_log_data = {
    'id':  session['user_id'],
    'log': 'User completed the questionnaire',
    'created_at': datetime.now()
    }
    Log.create_log(new_log_data)

    return jsonify(diagnosis)


@app.route('/blogs')
def blogs():
    
    blogs = Blog.get_all_blogposts()
    return render_template('blogs.html',blogs = blogs)

@app.route('/update_reminder', methods=['POST'])
def update_reminder():
    remind_status = request.form.get('remind')

    if 'user_id' in session:
        user_id = session['user_id']
        user = User.get_answers_by_user_id({'user_id': user_id})
        if user:
            data = {
                'id': user_id,
                'remind': remind_status
            }
            User.update_reminder(data)
            new_log_data = {
            'id':  session['user_id'],
            'log': 'User updated the reminder status',
            'created_at': datetime.now()
            }
            Log.create_log(new_log_data)
            send_daily_reminders()
            return redirect (request.referrer)
           
 

def send_reminder_email(email, name):
    msg = Message(
        subject='Reminder: Journal Entry Required',
        recipients=[email],
        html=(
            f"""
            <html>
              <body>
                <div style="font-family: Arial, sans-serif; color: #333;">
                  <h2 style="color: #4CAF50;">Dear {name},</h2>
                  <p>This is a friendly reminder that it's time to enter your daily journal entry. Maintaining your journal is an essential part of your mental wellness journey, and your regular entries help us provide you with better insights and support.</p>
                  
                  <p style="font-weight: bold;">Please take a moment to log in and record your thoughts and experiences for today.</p>
                  
                  <p>If you have any questions or need assistance, please do not hesitate to reach out to our support team.</p>
                  
                  <p>Thank you for your continued commitment to your well-being.</p>
                  <p>Best regards,<br>
                  The ZenZone Team<br>
                  <a href="mailto:zenzone@example.com">zenzone@example.com</a><br>
                  <a href="https://www.zenzone.com">www.zenzone.com</a></p>
                  
                  <img src="https://cdn.prod.website-files.com/64a593f0e89d3a52475b043e/64a5942a38b990c2af427e2e_zenzone-black.png" alt="ZenZone Logo" style="width: 150px;"/>
                </div>
              </body>
            </html>
            """
        )
    )
    mail.send(msg)




def send_daily_reminders():
    users =User.users_to_remind()
    for user in users:
        send_reminder_email(user['email'], user['first_name'])


def send_daily_reminders():
    batch_size = 100
    users =User.users_to_remind()
    for i in range(0, len(users), batch_size):
        batch = users[i:i+batch_size]
        for user in batch:
            send_reminder_email(user['email'], user['first_name'])
        time.sleep(5)  # Shmanget overload-i i serverit
 