from app.extensions import db, UserMixin
from werkzeug.security import check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    username = db.Column(
        db.String(12),
        nullable=False,
        unique=True,
    )
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    created_at = db.Column(db.Date, nullable=False)

    def __init__(self, first_name, last_name, username, email, password,
                 created_at):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at

    def register_user_if_not_exist(self):
        db_user = User.query.filter(
            User.username == self.username).first()  # Changed all() to first()
        if not db_user:
            db.session.add(self)
            db.session.commit()
            return True  # Return True after successful insertion
        return False  # Return False if user already exists

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_by_username(username):
        db_user = User.query.filter(User.username == username).first()
        return db_user

    @staticmethod
    def insert_user(first_name, last_name, username, email, password,
                    created_at):

        new_user = User(first_name=first_name,
                        last_name=last_name,
                        username=username,
                        email=email,
                        password=password,
                        created_at=created_at)
        db.session.add(new_user)
        db.session.commit()
        return new_user  # Return the newly created user object

    def __repr__(self):
        return f"<User {self.username}>"
