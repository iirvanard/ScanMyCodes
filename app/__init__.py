from flask import Flask,g
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf
from flask_migrate import Migrate
from dotenv import load_dotenv
import os 
from flask_login import current_user

load_dotenv()

# from celery import Celery,chain

from .workers import make_celery

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')


@app.before_request
def before_request():
    g.user = current_user

app.jinja_env.enable_async = True

app.config['STATIC_FOLDER_1'] = 'data'

app.config.update(CELERY_broker_url=os.getenv("CELERY_broker_url"),
                  result_backend=os.getenv("result_backend"))

celery = make_celery(app)

# Initialize configuration from CoolConfig
app.config.from_object(CoolConfig)

# Initialize db extension
db.init_app(app)

# Initialize CSRF
csrf.init_app(app)

# Initialize migration
migrate = Migrate(app, db)

# Initialize login manager after db
login_manager.init_app(app)

# Import model setelah inisialisasi ekstensi db
from app.models import *

# Import routes setelah inisialisasi aplikasi
from app import routes
