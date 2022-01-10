from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, AddFeedback
from sqlalchemy.exc import DatabaseError, IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():

    return redirect('/register')


@app.route('/register')
def render_register_form():
    form = RegisterForm()

    return render_template('register.html', form=form)


@app.route('/register', methods=["POST"])
def validate_register_form():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(
        username = form.username.data.lower(),
        password = form.password.data,
        email = form.email.data,
        first_name = form.first_name.data,
        last_name = form.last_name.data)

        temp = new_user.register(new_user.username, new_user.password)
        new_user.password = temp.password

        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        return redirect(f'/users/{new_user.username}')

    else:
        return redirect("/register")    


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
 
    return redirect('/')


@app.route('/users/<username>')
def user_detail(username):
    user = User.authorize(username)

    if user != "Do not have permission" or user != redirect('/login'):
        return render_template('userdetail.html', user=user)
    else:
        return user

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    user = User.authorize(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/')


@app.route('/users/<username>/feedback/add')
def add_feedback_form(username):
    form = AddFeedback()

    return render_template('addfeedback.html', form=form)


@app.route('/users/<username>/feedback/add', methods=["POST"])
def add_feedback(username):
    form = AddFeedback()    
    user = User.authorize(username)

    if user.username:
        if form.validate_on_submit:
            new_feedback = Feedback(
                title = form.title.data,
                content = form.content.data,
                username = user.username
            )

        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f'/users/{username}')
    
    else:
        return user


@app.route('/feedback/<feedbackid>/update', methods=["GET", "POST"])
def edit_feedback_form(feedbackid):
    feedback = Feedback.query.get_or_404(feedbackid)
    user = User.authorize(feedback.username)

    if user.username:
        form = AddFeedback(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return user



    

@app.route('/feedback/<feedbackid>/delete', methods=["POST"])
def delete_feedback(feedbackid):
    feedback = Feedback.query.get_or_404(feedbackid)
    user = User.authorize(feedback.username)

    if user.username:
        db.session.delete(feedback)
        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    else:
        return user
    