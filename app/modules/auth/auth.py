from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf.csrf import CSRFError  # Import CSRFError
from .auth_forms import LoginForm, RegistrationForm
from app.extensions import db, login_manager
from app.models.users import User

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_blueprint.route("/", methods=["GET"])
def auth_page():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    return render_template("auth.html")


@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        form = LoginForm(request.form)
        if form.validate():
            email_or_username = form.email_or_username.data.lower()
            password = form.password.data
            user = User.query.filter(db.or_(db.func.lower(User.email) == email_or_username, 
                                             db.func.lower(User.username) == email_or_username)).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index.index'))
            else:
                flash('Invalid email/username or password', 'error')
        else:
            flash('Invalid email/username or password', 'error')
        flash('', '_flashes')
        return redirect(url_for('auth.auth_page'))
    except CSRFError:
        flash('CSRF Token Error. Please try again.', 'error')
        return redirect(url_for('auth.auth_page'))


@auth_blueprint.route('/register', methods=['POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        if form.validate():
            email = form.email.data
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('auth.auth_page', _anchor='register'))
            hashed_password = generate_password_hash(form.password.data)
            user = User(first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        username=form.username.data,
                        password=hashed_password,
                        email=form.email.data,
                        created_at=datetime.now())
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('auth.auth_page'))
        else:
            flash('Registration failed. Please check your input.', 'error')
            return redirect(url_for('auth.auth_page', _anchor='register'))
    except CSRFError:
        return redirect(url_for('index.index'))


@auth_blueprint.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Logged out successfully', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('auth.auth_page'))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.auth_page'))
