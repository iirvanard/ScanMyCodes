import datetime

class User:
    def __init__(self, user_id, username, fullname, email, password, datetime_created):
        self.user_id = user_id
        self.username = username
        self.fullname = fullname
        self.email = email
        self.password = password
        self.datetime_created = datetime_created

    def __repr__(self):
        return f"User(id={self.user_id}, username='{self.username}', fullname='{self.fullname}', email='{self.email}', password='{self.password}', datetime_created='{self.datetime_created}')"
