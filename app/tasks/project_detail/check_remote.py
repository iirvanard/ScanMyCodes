import os
from app.extensions import db
from app.models import GitRepository, Project
from app import app,celery
from .database_manager import DatabaseManager
from .git_handler import GitHandler
from .scanning_project import scanning
from .logger import LoggerSetup
import logging



def process_project(id_project, log_file_path):
    """
    Process the project updates and log information.
    """
    project_log = DatabaseManager.add_project_log(id_project, log_file_path, log_type="update")
    return project_log

@celery.task()
def checkRemote(id_project):
    check_remote_task.delay(id_project=id_project)
    return "success trigger task"

@celery.task()
def check_remote_task(id_project):
    """
    Celery task to check for remote updates and log them.
    """
    try:
        project = Project.query.filter_by(project_id=id_project).first()

        # Konfigurasi logger
        logger_instance = LoggerSetup(id_project, project.project_name, "test1")

        logger, filename = logger_instance.get_logger()

        logger.info(filename)
        # Setup logging
        project_log = process_project(id_project, filename)
        
        # Retrieve repository information
        repository = GitRepository.query.filter_by(project_id=id_project).first()
        if not repository:
            raise ValueError(f"Repository for project ID {id_project} not found.")
        
        # Handle git operations
        git_handler = GitHandler(task_id=id_project, proj_url=repository.repo_url,
                                 access_token=repository.access_token, logger=logger)
        git_handler.check_for_update()

        # Optional scanning (commented out)
        # scanning(task_id=id_project, all_branches=git_handler.all_branch(basedir=repository.path_),
        #          dir_path=repository.path_, logger=logger, filename="c9b48348a57b4b7b9295951f7b75a026_20240723_203010_main.json")
        project_log.status="success"
        db.session.commit()
        return f"Project {id_project} successfully updated"

    except Exception as e:
        db.session.rollback()
        
        return f"An error occurred: {str(e)}"