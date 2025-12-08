from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Reads from .env file

app = Flask(__name__)

# Using SQLite for student simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///frogblogs-mm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'SECRET'

db = SQLAlchemy(app)

# ==========================
# DATABASE MODELS
# ==========================


class Blogs(db.Model):
    BlogID = db.Column(db.Integer, primary_key=True)
    BlogName = db.Column(db.String(80), nullable=False)
    BlogFrog = db.Column(db.Text(800), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey(
        'users.UserID'))
    comments = db.relationship('Comments', backref='blogs', lazy=True)

class Comments(db.Model):
    CommentID = db.Column(db.Integer, primary_key=True)
    CommentFrog = db.Column(db.Text(800), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey(
        'users.UserID'))
    BlogID = db.Column(db.Integer, db.ForeignKey(
        'blogs.BlogID'))

class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(80), nullable=False)
    blogs = db.relationship('Blogs', backref='users', lazy=True)
    comments = db.relationship('Comments', backref='users', lazy=True)

# ==========================
# ROUTES
# ==========================


@app.route('/')
def froghome():
    return render_template('froghome.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/blogs/add', methods=['GET', 'POST'])
def add_blog():
    users = Users.query.all()
    if request.method == 'POST':
        new_blog = Blogs(
            BlogName=request.form.get('blogName'),
            BlogFrog=request.form.get('blogFrog'),
            UserID=request.form.get('userid')
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('froghome'))
    return render_template('add_blog.html', users=users)

@app.route('/blogs/edit/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    users=Users.query.all()
    blog = Blogs.query.get_or_404(id)  
    if request.method == 'POST':
        blog.BlogName=request.form.get('blogName')
        blog.BlogFrog=request.form.get('blogFrog')
        blog.UserID=request.form.get('userid')
        db.session.commit()
        flash('Blog updated', 'success')
        return redirect(url_for('display_by_blog'))
    return render_template('add_blog.html', blog=blog, users=users)

@app.route('/blogs/delete/<int:id>')
def delete_blog(id):
    blog = Blogs.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog removed', 'success')
    return redirect(url_for('display_by_blog'))


@app.route('/comments/add/<int:blogid>', methods=['GET', 'POST'])
def add_comment(blogid):
    users = Users.query.all()  
    blog = Blogs.query.get_or_404(blogid)
    if request.method == 'POST':
        new_comment = Comments(
            CommentFrog=request.form['commentFrog'],
            UserID=request.form.get('userid'), 
            BlogID = blogid
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('display_by_blog'))
    return render_template('add_comment.html', users=users, blog=blog)

@app.route('/comments/edit/<int:id>', methods=['GET', 'POST'])
def edit_comment(id):
    users=Users.query.all()
    comment = Comments.query.get_or_404(id)  
    blog = Blogs.query.get_or_404(comment.BlogID)
    if request.method == 'POST':
        comment.CommentFrog=request.form['commentFrog']
        comment.UserID=request.form.get('userid') 
        db.session.commit()
        flash('Comment updated', 'success')
        return redirect(url_for('display_by_blog'))
    return render_template('add_comment.html', comment=comment, users=users, blog=blog)

@app.route('/comments/delete/<int:id>')
def delete_comment(id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment removed', 'success')
    return redirect(url_for('display_by_blog'))



@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = Users(
            UserName=request.form['userName']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('froghome'))
    return render_template('add_user.html')


@app.route('/blogs/view')
def display_by_blog():
    blogs = Blogs.query.all()
    return render_template('display_by_blog.html', blogs=blogs)


@app.route('/blogs/view/<int:id>')
def display_blog(id):
    blog = Blogs.query.get_or_404(id)
    return render_template('display_by_blog.html', blogs=[blog])


# Create DB if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
