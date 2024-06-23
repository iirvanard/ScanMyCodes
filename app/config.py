<<<<<<< HEAD
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()


=======
<<<<<<< HEAD
>>>>>>> 57a24e6 (before revisi)
class CoolConfig(object):
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@127.0.0.1:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
<<<<<<< HEAD
    SECRET_KEY = "kunciku"

=======
=======
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()


class CoolConfig(object):
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY =os.getenv('MY_SECRET_KEY') 

>>>>>>> 2fc3767 (before revision)
>>>>>>> 57a24e6 (before revisi)
