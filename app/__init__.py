from flask import Flask, g
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from flask_login import current_user
from sqlalchemy import create_engine, text

load_dotenv()

from .workers import make_celery

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

@app.before_request
def before_request():
    g.user = current_user

app.jinja_env.enable_async = True
app.config['STATIC_FOLDER_1'] = 'data'
app.config['RUNNER'] = 'runner'

app.config.update(
    CELERY_broker_url=os.getenv("CELERY_broker_url"),
    result_backend=os.getenv("result_backend")
)

celery = make_celery(app)

# Initialize configuration from CoolConfig
app.config.from_object(CoolConfig)

# Fungsi untuk membuat database jika belum ada
def create_database():
    db_url = CoolConfig.SQLALCHEMY_DATABASE_URI
    default_engine = create_engine(db_url.replace(f"/{os.getenv('POSTGRES_DB')}", "/postgres"), isolation_level="AUTOCOMMIT")  # ⬅️ Menjalankan di luar transaksi

    with default_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{os.getenv('POSTGRES_DB')}'"))
        exists = result.scalar()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {os.getenv('POSTGRES_DB')}"))  # ⬅️ Tidak akan terjebak dalam transaksi
            print(f"Database '{os.getenv('POSTGRES_DB')}' created successfully!")

# Panggil fungsi untuk memastikan database ada sebelum inisialisasi SQLAlchemy
create_database()

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
