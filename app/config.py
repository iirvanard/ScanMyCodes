from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()


class CoolConfig(object):
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@127.0.0.1:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "kunciku"
    CELERY_BROKER_URL= "redis://localhost:6379"

