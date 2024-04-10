from flask import render_template
from app import app

def about():
    # db_helper.execute_query("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(80) UNIQUE NOT NULL, email VARCHAR(120) UNIQUE NOT NULL);")
    # result = db_helper.execute_query("SELECT * FROM users")

    return "result"
