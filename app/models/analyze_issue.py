from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from .git_branch import GitBranch

class AnalyzeIssue(db.Model):
    __tablename__ = 'analyze_issue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey('projects.project_id',
                                         ondelete='CASCADE'),
                           nullable=False)
    branch = db.Column(db.String, nullable=False)
    path_ = db.Column(db.String, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    @validates('branch')
    def validate_branch(self, key, branch):
        if not GitBranch.query.filter_by(project_id=self.project_id, remote=branch).first():
            raise ValueError("Branch must exist in GitBranch table for the same project_id.")
        return branch