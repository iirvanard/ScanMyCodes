from flask import Flask
from app.config import CoolConfig
from app.extensions import db, login_manager, csrf
from flask_migrate import Migrate
# from .tasks import add
# from app.models.users import User
# from pygtail import Pygtail
# import time

from celery import Celery,chain

from .workers import make_celery


app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

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


# # Rute Flask untuk memicu tugas
# @app.route('/')
# def index():

#     return render_template('logs.html')


# # Rute Flask untuk memicu tugas
# @app.route('/add')
# def addx():
#     # Memanggil tugas Celery menggunakan metode delay
#     result = add.delay(3, 5)
#     return jsonify({'task_id': result.id})


# LOG_FILE = 'logs.log'


# @app.route('/progress')
# def progress():
#     def generate():
#         x = 0
#         while x <= 100:
#             yield "data:" + str(x) + "\n\n"
#             x = x + 10
#             time.sleep(0.5)
#     return Response(generate(), mimetype= 'text/event-stream')

# @app.route('/log')
# def progress_log():
# 	def generate():
# 		for line in Pygtail(LOG_FILE, every_n=1):
# 			yield str(line) + "\n\n"
# 			time.sleep(0.5)
# 	return Response(generate(), mimetype= 'text/event-stream')