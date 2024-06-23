from flask import Flask
<<<<<<< HEAD
=======
<<<<<<< HEAD
from flask_migrate import Migrate
>>>>>>> 57a24e6 (before revisi)
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
app.jinja_env.enable_async = True

app.config['STATIC_FOLDER_1'] = 'data'

app.config.update(CELERY_BROKER_URL='redis://localhost:6379',
                  CELERY_RESULT_BACKEND='redis://localhost:6379')
celery = make_celery(app)

# Initialize configuration from CoolConfig
app.config.from_object(CoolConfig)

# Initialize db extension
db.init_app(app)

# Initialize CSRF
csrf.init_app(app)

# Initialize migration
migrate = Migrate(app, db)

<<<<<<< HEAD
=======
=======
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf
from flask_migrate import Migrate
from dotenv import load_dotenv
import os 

load_dotenv()

# from celery import Celery,chain

from .workers import make_celery

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
app.jinja_env.enable_async = True

app.config['STATIC_FOLDER_1'] = 'data'

app.config.update(CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
                  CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND"))
celery = make_celery(app)

# Initialize configuration from CoolConfig
app.config.from_object(CoolConfig)

# Initialize db extension
db.init_app(app)

# Initialize CSRF
csrf.init_app(app)

# Initialize migration
migrate = Migrate(app, db)

>>>>>>> 57a24e6 (before revisi)
# Initialize login manager after db
login_manager.init_app(app)

# Import model setelah inisialisasi ekstensi db
from app.models import *

<<<<<<< HEAD
=======
>>>>>>> 2fc3767 (before revision)
>>>>>>> 57a24e6 (before revisi)
# Import routes setelah inisialisasi aplikasi
from app import routes
