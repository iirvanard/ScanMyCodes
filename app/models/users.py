from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
        db_user = User.query.filter(
            User.username == self.username).first()  # Changed all() to first()
        if not db_user:
            db.session.add(self)
            db.session.commit()
            return True  # Return True after successful insertion
        return False  # Return False if user already exists

    @staticmethod
    def get_by_username(username):
        db_user = User.query.filter(User.username == username).first()
        return db_user

    @staticmethod
    def insert_user(username, created_at, role):
        new_user = User(username=username, created_at=created_at, role=role)
        db.session.add(new_user)
        db.session.commit()
        return new_user  # Return the newly created user object

    def __repr__(self):
        return f"<User {self.username}>"
