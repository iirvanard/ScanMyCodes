import os
from app.extensions import db
from app.models import GitRepository, Project,ProjectCollaborator
from app import app, celery
from .database_manager import DatabaseManager
from .git_handler import GitHandler
from .scanning_project import scanning
from .logger import LoggerSetup
import logging


@celery.task()
def checkRemote(id_project, user_id):
    # Fetch project details
    project = Project.query.filter_by(project_id=id_project).first()
    if not project:
        return "Project not found"

    # Fetch collaborators for the project
    project_collaborators = ProjectCollaborator.query.filter_by(project_id=id_project).all()
    collaborator_ids = {collaborator.collaborator_id for collaborator in project_collaborators}

    # Check if user_id is either the project's user_id or one of the collaborator_ids
    if user_id == project.user_id or user_id in collaborator_ids:
        # Trigger the remote task
        check_remote_task.delay(id_project=id_project, user_id=user_id)
        return "Success trigger task"
    else:
        return "User is not authorized to check this project"


@celery.task()
def check_remote_task(id_project,user_id):
    """
    Celery task to check for remote updates and log them.
    """
    # Initialize the logger with a default logger in case of errors
    logger = logging.getLogger('default')
    logger.setLevel(logging.INFO)
    
    try:
        # Retrieve project and set initial status
        project = Project.query.filter_by(project_id=id_project).first()
        if not project:
            raise ValueError(f"Project with ID {id_project} not found.")
        
        project.fetch_status = "in_progress"
        project.analyze = "in_progress"
        db.session.commit()

        # Configure logger
        logger_instance = LoggerSetup(id_project, project.project_name, user_id)
        logger, filename = logger_instance.get_logger()
        logger.info(f"Logging initialized for project {id_project}")

        # Process project updates and log information
        project_log = DatabaseManager.add_project_log(task_id=id_project, log_file_path=filename, log_type="update", user_id=user_id) 
        
        # Retrieve repository information
        repository = GitRepository.query.filter_by(project_id=id_project).first()
        if not repository:
            raise ValueError(f"Repository for project ID {id_project} not found.")
        
        # Handle git operations
        git_handler = GitHandler(task_id=id_project, proj_url=repository.repo_url,
                                 access_token=repository.access_token, logger=logger)
        git_handler.check_for_update()

        # Optional scanning (commented out for now)
        # scanning(task_id=id_project, all_branches=git_handler.all_branch(basedir=repository.path_),
        #          dir_path=repository.path_, logger=logger, filename="c9b48348a57b4b7b9295951f7b75a026_20240723_203010_main.json")
        
        # Update project status and commit changes
        project_log.status = "success"
        project.fetch_status = "success"
        project.analyze = "success"
        db.session.commit()

        return f"Project {id_project} successfully updated"

    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        error_msg = f"An error occurred: {str(e)}"
        logger.error(error_msg)  # Log the error
        return error_msg
