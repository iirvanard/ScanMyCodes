from flask import Flask
from flask_migrate import Migrate
from app.config import CoolConfig
from app.extensions import db

# Import model setelah inisialisasi db
from app.models.users import User

app = Flask(__name__, template_folder='../templates')

# Inisialisasi konfigurasi dari CoolConfig
app.config.from_object(CoolConfig)

# Inisialisasi ekstensi db
db.init_app(app)

# Inisialisasi migrasi
migrate = Migrate(app, db)

# Import routes setelah inisialisasi aplikasi
from app import routes
