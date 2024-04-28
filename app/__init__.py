from flask import Flask
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf
from flask_migrate import Migrate
# from .tasks import add
# from app.models.users import User
# from pygtail import Pygtail
# import time

# from celery import Celery,chain

from .workers import make_celery


app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')


app.config['STATIC_FOLDER_1'] = 'data'

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
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

