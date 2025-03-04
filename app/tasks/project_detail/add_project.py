
import os
import uuid
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import celery, app
from app.extensions import db
from app.models import Project, ProjectLog,OpenaiProject,GitRepository


from .add_git_branch import addGitBranch
from .scanning_project import scanning
from .logger import LoggerSetup
from .git_handler import GitHandler
from .database_manager import DatabaseManager

class GitError(Exception):
    def __init__(self, message):
        self.message = message

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_2_database(self, user,privacy, proj_name, proj_url, description=None, access_token=None):
    task_id = celery.current_task.request.id
 
        # Konfigurasi logger
    logger_instance = LoggerSetup(task_id, proj_name, user)

    _, log_file_path = logger_instance.get_logger()


    __ = DatabaseManager.add_project(task_id=task_id, user_id=user, proj_name=proj_name, description=description)
    ___ = DatabaseManager.add_project_log(task_id, log_file_path,log_type="analyze",user_id=user)
    ____ = DatabaseManager.add_project_openai(task_id=task_id,openai_model=os.getenv('OPENAI_MODEL'),openai_key=os.getenv('OPENAI_KEY'),openai_url=os.getenv('OPENAI_BASE_URL'))
   
   
    return add.delay(task_id=task_id,privacy=privacy, proj_url=proj_url, proj_name=proj_name,log_file_path=log_file_path ,access_token =access_token)
@celery.task()
def add(task_id, privacy, proj_url, proj_name,log_file_path, access_token=None):
    try:
        log_path = os.path.join(app.config['STATIC_FOLDER_1'], "log",log_file_path)
        project_log = ProjectLog.query.filter_by(project_id=task_id,path_=log_file_path).first()

        logger =LoggerSetup.get_logger_filename(task_id=task_id,path=log_path)

        project_model = Project.query.filter_by(project_id=task_id).first()
        if not project_model:
            return "Project not found"

        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "repository", uuid.UUID(task_id).hex)
        git_handler = GitHandler(task_id=task_id, privacy=privacy, proj_url=proj_url, logger=logger, access_token=access_token)
        default_branch, all_branches = git_handler.clone_repository(dir_path)

        project_model.fetched_at = datetime.now()
        project_model.fetch_status = 'success'
        db.session.commit()

        repo = git_handler.add_repository_to_db(default_branch, dir_path)
        if repo:
            addGitBranch(task_id, all_branches, repo.id, logger)
            scanning(task_id, all_branches, dir_path, logger)

            DatabaseManager.update_project_status(project_model, 'success', analyze_at=datetime.now())
            db.session.commit()
            logger.info(f"Project {proj_name} analyzed successfully. [done]")

            project_log.status="success"
            db.session.commit()
            return "done"
        else:
            raise ValueError("Failed to add repository to the database.")

    except Exception as e:
        project_log.status="failed"

        if project_model:
            DatabaseManager.update_project_status(project_model, 'failed')
        
        db.session.commit()
        logger.error(f'{e} [failed]')
        return str(e)