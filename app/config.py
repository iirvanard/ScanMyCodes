from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()


class CoolConfig(object):
    POSTGRES_HOST = 'postgres' if os.getenv('FLASK_ENV') == 'production' else '127.0.0.1'
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{POSTGRES_HOST}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY =os.getenv('MY_SECRET_KEY') 

