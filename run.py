from app import app
from dotenv import load_dotenv
<<<<<<< HEAD
import os

if __name__ == "__main__":
=======
<<<<<<< HEAD

if __name__ == "__main__":
    HOST = load_dotenv('HOST') or '5000'
    PORT = load_dotenv('PORT') or '5000'
    DEBUG = load_dotenv('FLASK_DEBUG_MODE') or None
    app.run(host='0.0.0.0', port=5000)
=======
import os

if __name__ == "__main__":
>>>>>>> 57a24e6 (before revisi)
    load_dotenv()  # Load environment variables from .env file
   
    # Access environment variables using os.getenv
    HOST = os.getenv('HOST') or 'localhost'
    PORT = os.getenv('PORT') or '5000'
    DEBUG = os.getenv('FLASK_DEBUG_MODE')

    # Convert port to integer
    PORT = int(PORT)
    

    app.run(host=HOST, port=PORT, debug=DEBUG)
<<<<<<< HEAD
=======
>>>>>>> 2fc3767 (before revision)
>>>>>>> 57a24e6 (before revisi)
