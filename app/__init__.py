from flask import Flask
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf,celery
from flask_migrate import Migrate
from celery import Celery

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Inisialisasi konfigurasi dari CoolConfig
app.config.from_object(CoolConfig)

# Inisialisasi ekstensi db
db.init_app(app)

# csrf set
csrf.init_app(app)

# Inisialisasi migrasi
migrate = Migrate(app, db)

# Inisialisasi login manager setelah db
login_manager.init_app(app)


#celery 
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)



# Import model setelah inisialisasi ekstensi db
from app.models import *

# Import routes setelah inisialisasi aplikasi
from app import routes
