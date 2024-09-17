from flask_app import app
from flask import jsonify, render_template, redirect, session, request, flash
from flask_app.models.user import User
from flask_app.models.blogs import Blog
from flask_app.models.logs import Log
from flask_bcrypt import Bcrypt
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


@app.route('/addblogpost')
def addblogpost():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    return render_template('addblogpost.html', user=user)

@app.route('/addblogpost/new', methods=['POST'])
def new_blogpost():
    if 'user_id' not in session:
        return redirect('/')
    
    # Data for the blog post
    data = {
        'user_id': session['user_id'],
        'title': request.form['title'],
        'description': request.form['content'],
        'short_description': request.form['short_description']
    }
    
    # Create the blog post and get the blog ID
    blog_id = Blog.create_blogpost(data)
    
    # Save the image
    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
            image_data = {
                'image': image_filename,
                'blog_id': blog_id
            }
            Blog.save_image(image_data)
    
    #    # Save the files
    # if 'files' in request.files:
    #     file = request.files['files']
    #     if file and allowed_file(file.filename):
    #         file_content = file.read()  # Read the file content only once
    #         file_data = {
    #             'blog_id': blog_id,
    #             'FileName': secure_filename(file.filename),
    #             'FileType': file.content_type,
    #             'FileSize': len(file_content),  # Calculate file size
    #             'FileData': file_content,  # Store file content as binary
    #             'UploadDate': datetime.now()
    #         }
    #         Blog.save_file(file_data)
    
 
    
    return redirect('/addblogpost')


#SHOW ALL BLOG POSTS
@app.route('/blogposts')
def blogposts():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    return render_template('blogposts.html', user=user, blogposts = Blog.get_all_blogposts())


@app.route('/blogpost/<int:id>')
def blogpost(id):
   
    blog = Blog.get_blogpost_by_id({'id': id})
    return render_template('singlepost.html',  blog=blog)

@app.route('/loget')
def logs():  

    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/')       
    
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    return render_template('logs.html',  logs = Log.get_all_logs(), user=user)


 




