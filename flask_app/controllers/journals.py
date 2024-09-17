import joblib
from flask_app import app
from flask import render_template, redirect, session, request, flash
from flask_app.models.user import User
from flask_app.models.journal import Journal
from flask_app.models.logs import Log
from flask_bcrypt import Bcrypt
from datetime import datetime
from datetime import date
import joblib
import re
import string
from nltk.tokenize import word_tokenize


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


@app.route('/journals')
def journals():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    return render_template('journal.html', user=user, journals = Journal.get_all_journals())

# Load the SVM model and TF-IDF vectorizer
svm_model = joblib.load('flask_app/model/flask_app/model/svm_model.pkl')
tfidf_vectorizer = joblib.load('flask_app/model/flask_app/model/tfidf_vectorizer.pkl')

def preprocess(text):
    stop_words = open('C:/Users/Ralfi/Desktop/zenzone/flask_app/controllers/stopwords.txt', 'r', encoding='utf-8').read().split()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # Remove user @ references and '#' from text
    text = re.sub(r'\@\w+|\#', '', text)
    # Remove punctuations
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize and remove stopwords
    text_tokens = word_tokenize(text)
    text = [word.lower() for word in text_tokens if word.lower() not in stop_words]
    return " ".join(text)

@app.route('/journal/new', methods=['POST'])
def new_journal():
    if 'user_id' not in session:
        return redirect('/')

    description = request.form['description']
    
    # Preprocess the description
    cleaned_description = preprocess(description)
    
    # Transform the description using the TF-IDF vectorizer
    X = tfidf_vectorizer.transform([cleaned_description])
    
    # Predict sentiment
    prediction = svm_model.predict(X)
    
    sentiment = 'positive' if prediction[0] == 1 else 'negative'

    data = {
        'user_id': session['user_id'],
        'description': description,
        'rate': request.form['mood'],
        'title': request.form['entry-title'],
        'sentiment': sentiment  
    }
    # mood = data.get('mood')
    # if mood is None:
    #     flash("Ju duhet të zgjidhni një vlerësim të humorit. Faleminderit!!!.", 'warning')
    #     return redirect('/journals')
    
    if not Journal.validate_journal(data):
        return redirect('/journals')
    
    Journal.create_journal(data)
    new_log_data = {
    'id':  session['user_id'],
    'log': 'User completed the daily journal',
    'created_at': datetime.now()
    }
    Log.create_log(new_log_data)
    return redirect('/')



@app.route('/trackmood')
def trackmood():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    journals = Journal.get_all_journals()  
    mood_data = []
    sentiment_data = []
    dates = []

    for journal in journals:
        dates.append(journal['created_at'])  
        mood_data.append(journal['rate'])  
        if journal['annotation'] == 'positive':
            sentiment_data.append(1)
        elif journal['annotation'] == 'negative':
            sentiment_data.append(-1)
        else:
            sentiment_data.append(0)   
    return render_template('track.html', user=user, mood_data=mood_data, sentiment_data=sentiment_data, dates=dates)

@app.route('/insights')
def trackinsights():
    if 'user_id' not in session:
        return redirect('/')
    
    data = {'id': session['user_id']}
    user = User.get_user_by_id(data)
    journals = Journal.get_all_journals()

    mood_data = []
    sentiment_data = []
    dates = []

    total_rating = 0
    positive_count = 0
    rate_over_7_count = 0

    for journal in journals:
        dates.append(journal['created_at'].strftime('%Y-%m-%d'))  # Format the date
        rating = journal['rate']
        mood_data.append(rating)
        total_rating += rating

        if journal['annotation'] == 'positive':
            sentiment_data.append(1)
            positive_count += 1
        elif journal['annotation'] == 'negative':
            sentiment_data.append(-1)
        else:
            sentiment_data.append(0)   
        
        if rating > 7:
            rate_over_7_count += 1
 
    total_journals = len(journals)
    avg_mood_rating = total_rating / total_journals if total_journals > 0 else 0
    positive_sentiment_percentage = (positive_count / total_journals * 100) if total_journals > 0 else 0
    rate_over_7_percentage = (rate_over_7_count / total_journals * 100) if total_journals > 0 else 0

    return render_template('insights.html', 
                           user=user, 
                           mood_data=mood_data, 
                           sentiment_data=sentiment_data, 
                           dates=dates,
                           avg_mood_rating=avg_mood_rating,
                           positive_sentiment_percentage=positive_sentiment_percentage,
                           rate_over_7_percentage=rate_over_7_percentage)



@app.route('/evaluation')
def model_evaluation():
    results = Journal.calculate_precision_recall()
    return render_template('evaluation.html', results=results)
