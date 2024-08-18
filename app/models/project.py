from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db
import uuid

class Project(db.Model):
    __tablename__ = 'projects'

    project_id = db.Column(UUID(as_uuid=True),
                           primary_key=True,
                           default=uuid.uuid4,
                           unique=True)
    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.id', ondelete='CASCADE'),
                         nullable=False)
    fetch_status = db.Column(db.String, nullable=False, default='in_progress')
    analyze_status = db.Column(db.String, nullable=False, default='in_progress')
    analysis_request_at = db.Column(db.Date, default=datetime.now)
    description = db.Column(db.Text, nullable=True)
    project_name = db.Column(db.String(255), nullable=False)
    fetched_at = db.Column(db.Date, nullable=True)
    analyze_at = db.Column(db.Date, nullable=True)
    source = db.Column(db.String(50), nullable=False, default="git")
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
   
   
    openai_project = db.relationship('OpenaiProject', back_populates='project', uselist=False)

    user = db.relationship('User', back_populates='projects')

    branches = db.relationship('GitBranch', back_populates='project')

    ProjectLog = db.relationship("ProjectLog", back_populates="project")

    def __repr__(self):
        return f"<Project {self.project_id}>"
