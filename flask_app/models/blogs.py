from flask_app.config.mysqlconnection import connectToMySQL
import re	 
from flask import flash


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class Blog():
    db_name = 'diploma'
    def __init__(self, data):
        self.title = data['title']
        self.description = data['description']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def create_blogpost(cls, data):
        query = "INSERT INTO blogs (title, description,short_description) VALUES (%(title)s, %(description)s, %(short_description)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_blogposts(cls):
        query = "SELECT * FROM blogs join images on blogs.id= images.blog_id;"
        results = connectToMySQL(cls.db_name).query_db(query)
        blogs = []
        if results:
            for blog in results:
                blogs.append(blog)
            return blogs
        return blogs
    
    @classmethod
    def get_blogpost_by_id(cls, data):
        query = "SELECT blogs.*, images.image FROM blogs LEFT JOIN images ON blogs.id = images.blog_id WHERE blogs.id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    
    @classmethod
    def update_blogpost(cls, data):
        query = "UPDATE blogs SET title = %(title)s, description = %(description)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

    @classmethod
    def delete_blogpost(cls, data):
        query = "DELETE FROM blogs WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

    @classmethod
    def save_image(cls, data):
        query = "INSERT INTO images (image, blog_id) VALUES (%(image)s, %(blog_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    

    #save files in the files table
    @classmethod
    def save_file(cls, data):
        query = "INSERT INTO blogpostfiles (blog_id, FileName, FileType, FileSize, FileData, UploadDate) VALUES (%(blog_id)s, %(FileName)s, %(FileType)s, %(FileSize)s, %(FileData)s, %(UploadDate)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
