from flask import Flask, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(length=20), 
                        primary_key=True,
                        nullable=False, 
                        unique=True)
    password = db.Column(db.Text, 
                        nullable=False)
    email = db.Column(db.String(length=50),
                        nullable=False)
    first_name = db.Column(db.String(length=30), 
                        nullable=False) 
    last_name = db.Column(db.String(length=30), 
                        nullable=False)
                        
    feedback = db.relationship("Feedback", backref="users")

    @classmethod
    def register(cls, username, pwd):

        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, pwd):

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False

    @classmethod
    def authorize(cls, username):

        user = User.query.get_or_404(username)

        if 'username' not in session:
            flash("Please login")
            return redirect('/login')
        elif user.username != session['username']:
            return "Do not have permission"
        elif user.username == session['username']:
            return user
        else:
            return False
        




class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer(), 
                        primary_key=True,
                        autoincrement=True,
                        unique=True)
    title = db.Column(db.String(length=100),
                        nullable=False)
    content = db.Column(db.Text(), 
                        nullable=False) 
    username = db.Column(db.Text(),
                        db.ForeignKey('users.username', ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)