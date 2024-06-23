from flask_sqlalchemy import SQLAlchemy
<<<<<<< HEAD
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_wtf.csrf import CSRFProtect
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
celery = Celery()
=======
<<<<<<< HEAD

db = SQLAlchemy()
=======
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_wtf.csrf import CSRFProtect
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
celery = Celery()
>>>>>>> 2fc3767 (before revision)
>>>>>>> 57a24e6 (before revisi)
