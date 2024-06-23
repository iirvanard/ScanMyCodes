<<<<<<< HEAD
from datetime import datetime
from app.extensions import db, UserMixin
=======
<<<<<<< HEAD
from app.extensions import db
>>>>>>> 57a24e6 (before revisi)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
<<<<<<< HEAD
=======
    username = db.Column(db.String(), unique=True, nullable=False)
    created_at = db.Column(db.Date, nullable=False)
    role = db.Column(db.String(), default="employee")

    __table_args__ = (db.CheckConstraint(role.in_(
        ['student', 'teacher', 'employee']),
                                         name='role_types'), )

    def __init__(self, username, created_at, role):
        self.username = username
        self.created_at = created_at
        self.role = role

    def register_user_if_not_exist(self):
        db_user = User.query.filter(User.username == self.username).all()
        if not db_user:
            db.session.add(self)
            db.session.commit()

        return True

    def get_by_username(username):
        db_user = User.query.filter(User.username == username).first()
        return db_user
=======
from datetime import datetime
from app.extensions import db, UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
>>>>>>> 57a24e6 (before revisi)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    username = db.Column(
        db.String(12),
        nullable=False,
        unique=True,
    )
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
<<<<<<< HEAD
=======
>>>>>>> 2fc3767 (before revision)
>>>>>>> 57a24e6 (before revisi)

    def __repr__(self):
        return f"<User {self.username}>"
