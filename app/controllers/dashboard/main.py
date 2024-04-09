from flask import render_template
from app import app
from ...database.helper import DatabaseHelper

# Inisialisasi objek DatabaseHelper
db = DatabaseHelper()

def dashboard():
    """Rute untuk halaman about."""
    # Contoh eksekusi query database
    # result = db.execute_query("SELECT * FROM USER;")
    # Misalnya, Anda ingin merender hasil query di dalam template HTML
    # Anda bisa mengirimnya sebagai parameter ke render_template
    return "result"
