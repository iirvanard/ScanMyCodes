from flask import Blueprint, flash, request, render_template, redirect, url_for, session
from app.extensions import login_user, logout_user, login_required, login_manager
from .auth_forms import LoginForm, RegistrationForm
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_login import current_user
from flask_wtf.csrf import CSRFError  # Import CSRFError

from app.models.users import User

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@auth_blueprint.route("/", methods=["GET"])
def auth():
    if current_user.is_authenticated:  # Periksa apakah pengguna sudah login
        return redirect(
            url_for('index.index'))  # Arahkan ke halaman utama jika sudah
    return render_template("auth.html")


@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        form = LoginForm(request.form)
        if form.validate():
            email_or_username = form.email_or_username.data
            password = form.password.data
            user = User.query.filter((User.email == email_or_username) | (
                User.username == email_or_username)).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index.index'))
            else:
                flash('Invalid email/username or password', 'error')
        else:
            flash('Invalid email/username or password', 'error')
        flash('', '_flashes')

        return redirect(url_for('auth.auth'))
    except CSRFError:
        flash('CSRF Token Error. Please try again.', 'error')
    return redirect(url_for('auth.auth'))


@auth_blueprint.route('/register', methods=['POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        if form.validate():
            email = form.email.data
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('auth.auth', _anchor='register'))
            hashed_password = generate_password_hash(form.password.data)
            User.insert_user(first_name=form.first_name.data,
                             last_name=form.last_name.data,
                             username=form.username.data,
                             password=hashed_password,
                             email=form.email.data,
                             created_at=datetime.now())
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('auth.auth'))
        else:
            flash('Registration failed. Please check your input.', 'error')
            return redirect(url_for('auth.auth', _anchor='register'))
    except CSRFError:
        return redirect(url_for('index.index'))


@auth_blueprint.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Logged out successfully', 'success')
        return redirect(url_for('auth.auth'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('index.index'))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.auth'))
