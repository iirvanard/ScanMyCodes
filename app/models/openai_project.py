from datetime import datetime
from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class OpenaiProject(db.Model):
    __tablename__ = 'openai_project'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey('projects.project_id'),
                           nullable=False, unique=True)
    openai_model = db.Column(db.String, nullable=False)
    openai_key = db.Column(db.String, nullable=False)
    openai_url = db.Column(db.String, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    project = db.relationship('Project', back_populates='openai_project', uselist=False)
