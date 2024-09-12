from flask_app import app
from flask import jsonify, render_template, redirect, session, request, flash
from flask_app.models.user import User
from flask_app.models.blogs import Blog
from flask_app.models.diagnosis import Diagnosis
from flask_app.models.logs import Log
from flask_bcrypt import Bcrypt
from datetime import datetime
import datetime
from flask_app.config.mysqlconnection import connectToMySQL
import requests

from flask_mail import Mail, Message
from random import randint
from dotenv import load_dotenv
import os

load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


mail = Mail(app)

def verify_email(api_key, email):
    url = f'https://apps.emaillistverify.com/api/verifyEmail?secret={api_key}&email={email}'
    response = requests.get(url)
    return response.text
  


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

            return render_template('indexadminn.html', user_count=user_count, monthly_average=monthly_average, active_users=active_users)
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
    
    # Generate verification code
    verification_code = randint(100000, 999999)  # 6-digit random code
    
    # Temporarily store user data
    session['user_data'] = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'confirm_password': bcrypt.generate_password_hash(request.form['confirm_password']),
        'age': request.form['age'],
        'role': 'user',
        'verification_code': verification_code,  # Store verification code
     }
    
    # Call the email verification API
    api_key = os.getenv('API_KEY')
    email = request.form['email']
    result = verify_email(api_key, email)

    if result == "ok":
        send_verification_email(email, verification_code)      
        flash('A verification code has been sent to your email. Please enter the code to complete registration.', 'success')
        return redirect('/verify')

    flash('Your email is not valid!', 'emailSignUp')
    return redirect(request.referrer)


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
            
                
                flash('Your account has been successfully verified and created!', 'success')
                return redirect('/')
            else:
                flash('Invalid verification code. Please try again.', 'error')
    
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
    
    #User.delete_answers({'user_id': session['user_id']})
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

 