from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID


class GitRepository(db.Model):
    __tablename__ = 'git_repository'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    privacy = db.Column(db.Boolean, nullable=False)
    access_token = db.Column(db.String, nullable=True)
    repo_url = db.Column(db.String, nullable=False)
    default_branch = db.Column(db.String(30), nullable=True)
    project_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey('projects.project_id',
                                         ondelete='CASCADE'),
                           unique=True,
                           nullable=False)
    path_ = db.Column(db.String, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
