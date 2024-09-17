from flask_app.config.mysqlconnection import connectToMySQL
import re	 
from flask import flash


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User():
    db_name = 'diploma'
    def __init__(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.age = data['age'] 
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.role = data['role']


    @classmethod
    def get_latest_answer_date(cls, data):
        query = 'SELECT createdAt FROM answers WHERE user_id = %(user_id)s ORDER BY createdAt DESC LIMIT 1;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]['createdAt']
        return None


    @classmethod
    def create_user(cls, data):
        query = "INSERT INTO users (first_name, last_name,age,email, password,role) VALUES (%(first_name)s, %(last_name)s,%(age)s,%(email)s, %(password)s,%(role)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
        
    @classmethod
    def update_diagnosis(cls, data):
        query = "INSERT INTO diagnosis (user_id, diagnosis) VALUES (%(user_id)s, %(diagnosis)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
     
    
   



    
    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @staticmethod
    def validate_user(data):
        is_valid = True
        if len(data['first_name']) < 2:
            flash("First name must be at least 2 characters.", 'first_name')
            is_valid = False
        if len(data['last_name']) < 2:
            flash("Last name must be at least 2 characters.", 'last_name')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address!", 'emailSignUp')
            is_valid = False
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters.", 'passwordSignUp')
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash("Passwords do not match!", 'passwordSignUp')
            is_valid = False
        return is_valid
    
    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    

    @classmethod
    def get_all_users(cls):
        query = 'SELECT * FROM users;'
        results = connectToMySQL(cls.db_name).query_db(query)
        users= []
        if results:
            for user in results:
                users.append(user)
            return users
        return users
    
    @classmethod
    def update_user(cls, data):
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, age = %(age)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

    @classmethod
    def update_profile_pic_user(cls, data):
        query = "UPDATE users SET profile_pic = %(image)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    


    @classmethod
    def get_questions(cls):
        query = 'SELECT * FROM questions;'
        results = connectToMySQL(cls.db_name).query_db(query)
        questions = []
        if results:
            for question in results:
                questions.append(question)
            return questions
        return questions
    

    @classmethod
    def get_options_of_question(cls, data):
        query = 'SELECT * FROM options WHERE question_id = %(question_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        options = []
        if results:
            for option in results:
                options.append(option)
            return options
        return options
    
    @classmethod
    def options_of_all_questions(cls):
        query = 'SELECT * FROM options;'
        results = connectToMySQL(cls.db_name).query_db(query)
        options = []
        if results:
            for option in results:
                options.append(option)
            return options
        return options
    
    @classmethod
    def add_answer(cls, data):
        query = "INSERT INTO answers (user_id, question_id, answer) VALUES (%(user_id)s, %(question_id)s, %(answer)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_questions_with_options(cls):
        query = 'SELECT * FROM questions JOIN options ON questions.id = options.question_id;'
        results = connectToMySQL(cls.db_name).query_db(query)
        questions = []
        if results:
            for question in results:
                questions.append(question)
            return questions
        return questions
    
    @classmethod
    def get_answers_by_user_id(cls, data):
        query = 'SELECT * FROM answers WHERE user_id = %(user_id)s ORDER BY createdAt DESC LIMIT 20;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        answers = []
        if results:
            for answer in results:
                answers.append(answer)
            return answers
        return answers
    
    @classmethod
    def delete_answers(cls, data):
        query = 'DELETE FROM answers WHERE user_id = %(user_id)s;'
        return connectToMySQL(cls.db_name).query_db(query, data)

    
    #get 20latest answers of user
    @classmethod
    def get_latest_answers(cls, data):
        query = 'SELECT * FROM answers WHERE user_id = %(user_id)s ORDER BY created_at DESC LIMIT 20;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        answers = []
        if results:
            for answer in results:
                answers.append(answer)
            return answers
        return answers
    

    @classmethod
    def get_latest_diagnosis(cls, data):
        query = 'SELECT * FROM diagnosis WHERE user_id = %(user_id)s ORDER BY createdAt DESC LIMIT 1;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    

    @classmethod
    def get_all_diagnosis(cls, data):
        query = 'SELECT * FROM diagnosis WHERE user_id = %(user_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        diagnosis = []
        if results:
            for diag in results:
                diagnosis.append(diag)
            return diagnosis
        return diagnosis
    
 
    @classmethod
    def number_of_users(cls):
        query = 'SELECT COUNT(*) FROM users;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    

    @classmethod
    def monthly_average_of_journals_per_user(cls):
        query = 'SELECT COUNT(*) FROM journals  '
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    

    @classmethod
    def active_users(cls):
        query = '''
    SELECT COUNT(*) AS active_user_count
        FROM users
        WHERE id IN (
            SELECT user_id
            FROM journals
            WHERE DATE(created_at) = CURDATE() OR DATE(created_at) = CURDATE() - INTERVAL 1 DAY
            GROUP BY user_id
             
                );
        '''
        results = connectToMySQL(cls.db_name).query_db(query)
        
        if results:
            return results[0]['active_user_count'] if 'active_user_count' in results[0] else 0
        return 0
    
    @classmethod
    def update_reminder(cls, data):
        query = "UPDATE users SET remind = %(remind)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)


 
    #metode qe kthen te gjithe userat qe duhet te rikujtohen per te shkruar ditar
    #kjo metode do te thirret cdo dite nga admini
    @classmethod
    def users_to_remind(cls):
        query = '''SELECT * FROM users WHERE remind = 'yes' AND id NOT IN (SELECT user_id FROM journals WHERE DATE(created_at) = CURDATE()
         GROUP BY user_id);'''
        results = connectToMySQL(cls.db_name).query_db(query)
        users = []
        if results:
            for user in results:
                users.append(user)
            return users
        return users 
 

    @classmethod
    def low_mood_users(cls):
        query = '''SELECT * FROM users WHERE id IN (SELECT user_id FROM (
        SELECT user_id, rate, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn 
        FROM journals
    ) AS last_journals
    WHERE rn <= 7
    GROUP BY user_id
    HAVING COUNT(*) = 1 AND MAX(rate) < 5);'''
        results = connectToMySQL(cls.db_name).query_db(query)
        users = []
        if results:
            for user in results:
                users.append(user)
            return users

 
 
    

    