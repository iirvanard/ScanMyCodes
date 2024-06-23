from app import app
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
   
    # Access environment variables using os.getenv
    HOST = os.getenv('HOST') or 'localhost'
    PORT = os.getenv('PORT') or '5000'
    DEBUG = os.getenv('FLASK_DEBUG_MODE')

    # Convert port to integer
    PORT = int(PORT)
    

    app.run(host=HOST, port=PORT, debug=DEBUG)
