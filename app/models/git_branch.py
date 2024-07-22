from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID

class GitBranch(db.Model):
    __tablename__ = 'git_branch'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    remote = db.Column(db.String, nullable=False)
    project_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('projects.project_id',
                                        ondelete='CASCADE'),
                        nullable=False)
    git_repository_id=  db.Column(db.Integer,
                           db.ForeignKey('git_repository.id',
                                         ondelete='CASCADE'),  
                           nullable=False)
    project = db.relationship('Project', back_populates='branches')
    
    # Menambahkan kolom last_analyze_at
    last_analyze_at = db.Column(db.DateTime, nullable=True)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    @property
    def last_analyze_at(self):
        if self.project:
            return self.project.analyze_at
        return None
    
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'remote', name='_project_remote_uc'),
    )