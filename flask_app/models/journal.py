from flask_app.config.mysqlconnection import connectToMySQL
import re	 
from flask import flash
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class Journal():
    
    db_name = 'diploma'
    def __init__(self, data):
        self.description = data['description']
        self.user_id = data['user_id']
        self.rate = data['rate']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.annotation = data['annotation']
    
    @classmethod
    def create_journal(cls, data):
        query = "INSERT INTO journals (description, user_id, rate,annotation,title) VALUES ( %(description)s, %(user_id)s, %(rate)s,%(sentiment)s,%(title)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_journals(cls):
        query = "SELECT * FROM journals;"
        results = connectToMySQL(cls.db_name).query_db(query)
        journals = []
        if results:
            for journal in results:
                journals.append(journal)
            return journals
        return journals
    
    @classmethod
    def get_journal_by_id(cls, data):
        query = "SELECT * FROM journals WHERE id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def update_journal(cls, data):
        query = "UPDATE journals SET title = %(title)s, content = %(content)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete_journal(cls, data):
        query = "DELETE FROM journals WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @staticmethod
    def validate_journal(data):
        is_valid = True
        if len(data['description']) < 5:
            flash("PERSHKRIMI JUAJ DUHET TE JETE ME TEPER SE SE NJE FJALE.Faleminderit!!!.", 'content')
            is_valid = False
        # if not data.get('mood'):
        #     flash("Ju duhet të zgjidhni një vlerësim të humorit. Faleminderit!!!.", 'warning')
        #     is_valid = False
        return is_valid
    
    @staticmethod
    def has_journal_today(cls,user_id):
        query = "SELECT * FROM journals WHERE user_id = %(id)s AND DATE(created_at) = CURDATE();"
        result = connectToMySQL(cls.db_name).query_db(query, [user_id])
        return len(result) > 0
    

    @classmethod
    def last_journal(cls,user_id):
        query = "SELECT * FROM journals WHERE user_id = %(id)s ORDER BY created_at DESC LIMIT 1;"
        result = connectToMySQL(cls.db_name).query_db(query, [user_id])
        if result:
            return result[0]
        return False
    


    @classmethod
    def calculate_precision_recall(cls):
        query_tp = "SELECT COUNT(*) as count FROM journals WHERE rate > 5 AND annotation = 'positive';"
        query_tn = "SELECT COUNT(*) as count FROM journals WHERE rate <= 5 AND annotation = 'negative';"
        query_fp = "SELECT COUNT(*) as count FROM journals WHERE rate <= 5 AND annotation = 'positive';"
        query_fn = "SELECT COUNT(*) as count FROM journals WHERE rate > 5 AND annotation = 'negative';"

        true_positives = connectToMySQL(cls.db_name).query_db(query_tp)[0]['count']
        true_negatives = connectToMySQL(cls.db_name).query_db(query_tn)[0]['count']
        false_positives = connectToMySQL(cls.db_name).query_db(query_fp)[0]['count']
        false_negatives = connectToMySQL(cls.db_name).query_db(query_fn)[0]['count']

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        accuracy = (true_positives+true_negatives) / (true_positives +true_negatives+ false_positives+false_negatives) if(true_positives +true_negatives+ false_positives+false_negatives) > 0 else 0
        return {
            'precision': precision,
            'recall': recall,
            'accuracy': accuracy,
            'true_positives': true_positives,
            'true_negatives': true_negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    @classmethod
    def get_filtered_journals(cls, user_id, start_date=None, end_date=None, mood_filter=None, sentiment_filter=None):
        # Base query
        query = "SELECT * FROM journals WHERE user_id = %(user_id)s"
        params = {'user_id': user_id}

        # Add filters
        if start_date:
            query += " AND created_at >= %(start_date)s"
            params['start_date'] = start_date
        if end_date:
            query += " AND created_at <= %(end_date)s"
            params['end_date'] = end_date
        if mood_filter:
            query += " AND rate = %(mood_filter)s"
            params['mood_filter'] = mood_filter
        if sentiment_filter:
            sentiment_map = {'1': 'positive', '-1': 'negative'}
            sentiment = sentiment_map.get(sentiment_filter, None)
            if sentiment:
                query += " AND annotation = %(sentiment_filter)s"
                params['sentiment_filter'] = sentiment

        # Execute the query
        result = connectToMySQL(cls.db_name).query_db(query, params)
        return result


    
  
