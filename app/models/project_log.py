from datetime import datetime
from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ProjectLog(db.Model):
    __tablename__ = 'project_log'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey('projects.project_id'),
                           nullable=False)
    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.id', ondelete='CASCADE'),
                         nullable=False)
    type = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    path_ = db.Column(db.String, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', back_populates='ProjectLog')
    
    project = db.relationship("Project", back_populates="ProjectLog")
