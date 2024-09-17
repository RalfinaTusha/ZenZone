import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import re
import string
from nltk.tokenize import word_tokenize
import nltk
import joblib

# Download necessary NLTK data
nltk.download('punkt')

# Load the Review Dataset
df_review = pd.read_csv("review.csv")

# Preprocess the Review Data
def preprocess(text):
    stop_words = open('stopwords.txt','r', encoding='utf-8').read().split()
    # Remove urls
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # Remove user @ references and '#' from text
    text = re.sub(r'\@\w+|\#','', text)
    # Remove punctuations
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize and remove stopwords
    text_tokens = word_tokenize(text)
    text = [word.lower() for word in text_tokens if word.lower() not in stop_words]
    return " ".join(text)

df_review['Clean_text'] = df_review['Review'].apply(preprocess)

# TF-IDF Vectorization
tfidf_vectorizer = TfidfVectorizer()
X = tfidf_vectorizer.fit_transform(df_review['Clean_text'])
y = df_review['Polarity']

# Split the Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the SVM Model
svm_model = SVC(kernel='linear')
svm_model.fit(X_train, y_train)

 
# Save the Model and Vectorizer
joblib.dump(svm_model, 'flask_app/model/svm_model.pkl')
joblib.dump(tfidf_vectorizer, 'flask_app/model/tfidf_vectorizer.pkl')

 

