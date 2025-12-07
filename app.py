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
    BlogFrog = db.Column(db.String(800), nullable=False)
    memberships = db.relationship('Memberships', backref='blog', lazy=True)
    users = db.relationship('Users', backref='blog', lazy=True)


class Comments(db.Model):
    CommentID = db.Column(db.Integer, primary_key=True)
    CommentFrog = db.Column(db.String(80), nullable=False)
    memberships = db.relationship('Memberships', backref='comment', lazy=True)

class Memberships(db.Model):
    MembershipID = db.Column(db.Integer, primary_key=True)
    BlogID = db.Column(db.Integer, db.ForeignKey(
        'blogs.BlogID'), nullable=False)
    CommentID = db.Column(db.Integer, db.ForeignKey(
        'comments.CommentID'), nullable=False)
    StartYear = db.Column(db.Integer)
    EndYear = db.Column(db.Integer)  # NULL if still active
    Role = db.Column(db.Text)


class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    BlogID = db.Column(db.Integer, db.ForeignKey(
        'blogs.BlogID'))
    UserName = db.Column(db.String(80))

# ==========================
# ROUTES
# ==========================


@app.route('/')
def froghome():
    return render_template('froghome.html')

@app.route('/blogs/add', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'POST':
        new_blog = Blogs(
            BlogName=request.form['blogName'],
            BlogFrog=request.form['blogFrog']
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('froghome'))
    return render_template('add_blog.html')

@app.route('/comments/add', methods=['GET', 'POST'])
def add_comment():
    blogs = Blogs.query.all()  
    if request.method == 'POST':
        new_comment = Comments(
            CommentFrog=request.form['commentFrog'],
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('froghome'))
    return render_template('add_comment.html', blogs=blogs)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    blogs = Blogs.query.all()
    if request.method == 'POST':
        new_user = Users(
            UserName=request.form['userName']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('froghome'))
    return render_template('add_user.html', blogs=blogs)


@app.route('/blogs/view')
def display_by_blog():
    blogs = Blogs.query.all()
    return render_template('display_by_blog.html', blogs=blogs)


@app.route('/blogs/view/<int:id>')
def display_blog(id):
    blog = Blogs.query.get_or_404(id)
    return render_template('display_by_blog.html', blogs=[blog])


@app.route('/memberships/add', methods=['GET', 'POST'])
def add_commenttoblog():
    blogs = Blogs.query.all()
    comments = Comments.query.all()
    if request.method == 'POST':
        membership = Memberships(
            BlogID=request.form.get('blogid'),
            CommentID=request.form.get('commentid'),
            Role=request.form.get('role'),
            StartYear=request.form.get('startyear') or None,
            EndYear=request.form.get('endyear') or None
        )
        db.session.add(membership)
        db.session.commit()
        flash('Membership assigned', 'success')
        return redirect(url_for('display_by_blog'))
    return render_template('add_commenttoblog.html', blogs=blogs, comments=comments)



@app.route('/memberships/edit/<int:id>', methods=['GET', 'POST'])
def edit_membership(id):
    membership = Memberships.query.get_or_404(id)
    blogs = Blogs.query.all()
    comments = Comments.query.all()
    if request.method == 'POST':
        membership.BlogID = request.form.get('blogid')
        membership.CommentID = request.form.get('commentid')
        membership.Role = request.form.get('role')
        membership.StartYear = request.form.get('startyear') or None
        membership.EndYear = request.form.get('endyear') or None
        db.session.commit()
        flash('Comment updated', 'success')
        return redirect(url_for('display_by_blog'))

    return render_template('add_commenttoblog.html', membership=membership, blogs=blogs, comments=comments)


@app.route('/memberships/delete/<int:id>')
def delete_membership(id):
    membership = Memberships.query.get_or_404(id)
    db.session.delete(membership)
    db.session.commit()
    flash('Comment removed', 'success')
    return redirect(url_for('display_by_blog'))


# Create DB if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
