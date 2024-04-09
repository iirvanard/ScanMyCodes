from app import app
from dotenv import load_dotenv

if __name__ == "__main__":
    HOST = load_dotenv('HOST') or '5000'
    PORT = load_dotenv('PORT') or '5000'
    DEBUG = load_dotenv('FLASK_DEBUG_MODE') or None
    app.run()

