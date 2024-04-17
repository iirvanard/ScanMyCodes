from flask import Flask
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf
from flask_migrate import Migrate

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


# Define user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Import model setelah inisialisasi ekstensi db
from app.models.users import User
from app.models.project import Project

# Import routes setelah inisialisasi aplikasi
from app import routes
