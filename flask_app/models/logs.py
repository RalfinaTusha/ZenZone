from flask_app.config.mysqlconnection import connectToMySQL
import re	 
from flask import flash


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class Log():
    db_name = 'diploma'
    def __init__(self, data):
        self.log = data['log']
        self.user_id = data['user_id']
        self.created_at = data['created_at']


    @classmethod
    def create_log(cls, data):
        query = "INSERT INTO logs (user_id, log) VALUES (%(id)s, %(log)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_logs(cls):
        query = "SELECT logs.*, users.email AS created_by FROM logs LEFT JOIN users ON logs.user_id = users.id;"
        results = connectToMySQL(cls.db_name).query_db(query)
        logs = []
        if results:
            for log in results:
                logs.append(log)
            return logs
        return logs
    
 
 