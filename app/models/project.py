from app.extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80),
                         db.ForeignKey('users.username'),
                         nullable=False)
    git_urls = db.Column(db.String, nullable=False)
    last_update = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.Date, nullable=False)

    def __init__(self, username, git_urls, last_update, created_at):
        self.username = username
        self.git_urls = git_urls
        self.last_update = last_update
        self.created_at = created_at

    @staticmethod
    def get_by_username(username):
        return Project.query.filter_by(username=username).first()

    @staticmethod
    def insert_project(username, git_urls, last_update, created_at):
        new_project = Project(username=username,
                              git_urls=git_urls,
                              last_update=last_update,
                              created_at=created_at)
        db.session.add(new_project)
        db.session.commit()
        return new_project

    def __repr__(self):
        return f"<Project {self.id}>"
