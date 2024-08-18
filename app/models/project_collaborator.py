from datetime import datetime
from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint

class ProjectCollaborator(db.Model):
    __tablename__ = 'project_collaborators'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.project_id'), nullable=False)
    collaborator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')



    accesses = db.relationship('CollaboratorAccess', back_populates='collaborator')

    project = db.relationship('Project', backref='project_collaborators', lazy=True)


    # Mendefinisikan relasi untuk collaborator
    collaborator = db.relationship('User', foreign_keys=[collaborator_id], backref='collaborator_projects', lazy=True)

    # Mendefinisikan relasi untuk inviter
    inviter = db.relationship('User', foreign_keys=[inviter_id], backref='inviter_projects', lazy=True)


    __table_args__ = (
        UniqueConstraint('project_id', 'collaborator_id', name='unique_project_collaborator'),
    )
    
    def confirm(self):
        self.status = 'confirmed'
        db.session.commit()

        
    def rejected(self):
        self.status = 'rejected'
        db.session.commit()