from app.extensions import db
from app.models import GitRepository, OpenaiProject, Project
from app import celery

@celery.task()
def checkRemote():
    try:
        return "Project updated successfully"
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}"
