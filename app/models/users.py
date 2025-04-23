from datetime import datetime
from app.extensions import db, UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    image_profile =db.Column(db.String(2048), nullable=True)
    username = db.Column(
        db.String(12),
        nullable=False,
        unique=True,
    )
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    projects = db.relationship('Project', back_populates='user')

    ProjectLog = db.relationship('ProjectLog', back_populates='user')


    def __repr__(self):
        return f"<User {self.username}>"
