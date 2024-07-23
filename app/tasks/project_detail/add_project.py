
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
class GitError(Exception):
    def __init__(self, message):
        self.message = message

class DatabaseManager:
    @staticmethod
    def add_project(task_id, user, proj_name, description):
        project_model = Project(project_id=task_id, username=user, project_name=proj_name, description=description)
        try:
            with db.session.begin_nested():
                db.session.add(project_model)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            project_model = Project.query.filter_by(project_id=task_id).first()
        return project_model

    @staticmethod
    def add_project_log(task_id, log_file_path):
        project_log = ProjectLog(project_id=task_id, type="analyze", status="on progress", path_=log_file_path)
        with db.session.begin_nested():
            db.session.add(project_log)
        db.session.commit()
        return project_log

    @staticmethod
    def update_project_status(project_model, status, fetched_at=None, analyze_at=None):
        project_model.analyze_status = status
        if fetched_at:
            project_model.fetched_at = fetched_at
        if analyze_at:
            project_model.analyze_at = analyze_at
        db.session.commit()

    @staticmethod
    def add_project_openai(task_id, openai_model,openai_key,openai_url):
        project_openai = OpenaiProject(project_id=task_id, openai_model=openai_model,openai_key=openai_key,openai_url=openai_url)
        with db.session.begin_nested():
            db.session.add(project_openai)
        db.session.commit()
        return project_openai

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_2_database(self, user,privacy, proj_name, proj_url, description=None, access_token=None):
    task_id = celery.current_task.request.id
    
    logger_setup = LoggerSetup(task_id, proj_name, user)
    _, log_file_path = logger_setup.get_logger()

    __ = DatabaseManager.add_project(task_id, user, proj_name, description)
    project_log = DatabaseManager.add_project_log(task_id, log_file_path)
    ___ = DatabaseManager.add_project_openai(task_id=task_id,openai_model=os.getenv('OPENAI_MODEL'),openai_key=os.getenv('OPENAI_KEY'),openai_url=os.getenv('OPENAI_BASE_URL'))
   
   
    return add.delay(task_id=task_id,privacy=privacy, proj_url=proj_url, log_id=project_log.id, proj_name=proj_name, access_token =access_token)

@celery.task()
def add(task_id, privacy,proj_url, log_id, proj_name, access_token=None):
    try:
        project_log = ProjectLog.query.filter_by(id=log_id).first()
        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log",project_log.path_)

        logger = logging.getLogger(task_id)
        if not logger.handlers:
            fh = logging.FileHandler(dir_path)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)
    
        project_model = Project.query.filter_by(project_id=task_id).first()
        if not project_model:
            logger.error(f"Project with task ID {task_id} not found in the database.  [failed]")
            return
        
        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "repository", uuid.UUID(task_id).hex)
        git_handler = GitHandler(task_id=task_id,privacy=privacy, proj_url=proj_url, logger=logger,access_token=access_token)
        default_branch, all_branches = git_handler.clone_repository(dir_path)

        project_model.fetched_at = datetime.now()
        project_model.fetch_status = 'success'
        db.session.commit()

        repo = git_handler.add_repository_to_db(default_branch, dir_path)
        if repo:
            addGitBranch(task_id, all_branches, repo.id, logger)
            scanning(task_id, all_branches, dir_path, logger)

            DatabaseManager.update_project_status(project_model, 'success', analyze_at=datetime.now())
            project_log.status = 'success'
            db.session.commit()
            logger.info(f"Project {proj_name} analyzed successfully. [done]")
        else:
            raise ValueError("Failed to add repository to the database.")

    except Exception as e:
        if project_model:
            DatabaseManager.update_project_status(project_model, 'failed')
        if project_log:
            project_log.status = 'failed'
        db.session.commit()
        
        logger.error(f'{e} [failed]')

    return "done"
