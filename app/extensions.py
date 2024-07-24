from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy(session_options={"autoflush": False})
login_manager = LoginManager()
csrf = CSRFProtect()
celery = Celery()
