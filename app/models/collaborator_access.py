from datetime import datetime
from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint



class CollaboratorAccess(db.Model):
    __tablename__ = 'collaborator_access'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collaborator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('project_collaborators.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('git_branch.id', ondelete='CASCADE'), nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)


    collaborator = db.relationship('ProjectCollaborator', back_populates='accesses')
    

    branch = db.relationship('GitBranch', back_populates='collaborator_access')

    # Ensure unique (collaborator_id, branch_id) pairs
    __table_args__ = (
        UniqueConstraint('collaborator_id', 'branch_id', name='unique_collaborator_branch'),
    )
