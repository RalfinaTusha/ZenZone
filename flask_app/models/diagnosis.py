from flask_app.config.mysqlconnection import connectToMySQL
import re	 
from flask import flash


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class Diagnosis():
    db_name = 'diploma'
    def __init__(self, data):
        self.diagnosis = data['diagnosis']
        self.user_id = data['user_id']
        self.CreatedAt = data['CreatedAt']
 

    @classmethod
    def create_diagnosis(cls, data):
        query = "INSERT INTO diagnosis (user_id, diagnosis) VALUES (%(id)s, %(diagnosis)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_diagnosis(cls):
        query = "SELECT * FROM diagnosis;"
        results = connectToMySQL(cls.db_name).query_db(query)
        diagnosis = []
        if results:
            for diag in results:
                diagnosis.append(diag)
            return diagnosis
        return diagnosis
    
    @classmethod
    def get_diagnosis_by_id(cls, data):
        query = "SELECT * FROM diagnosis WHERE id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def update_diagnosis(cls, data):
        query = "UPDATE diagnosis SET diagnosis = %(diagnosis)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_latest_diagnosis(cls, data):
        query = 'SELECT * FROM diagnosis WHERE user_id = %(id)s ORDER BY CreatedAt DESC LIMIT 1;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]['diagnosis']
        return None