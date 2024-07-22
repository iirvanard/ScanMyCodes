
import os
import uuid
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import celery, app
from app.extensions import db
from app.models import Project,  ProjectLog
from app.models.git_repository import GitRepository
from app.utils.git_core import GitUtils
from app.utils.utils import split_url

from .cloning_project import cloning
from .scanning_project import scanning
from .logger import LoggerSetup

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

class GitHandler:
    def __init__(self, task_id, proj_url, logger,privacy, access_token=None):
        self.task_id = task_id
        self.proj_url = proj_url
        self.logger = logger
        self.privacy = privacy
        self.access_token = access_token

    def clone_repository(self, dir_path):
        repo_owner, repo_name = split_url(self.proj_url)
        self.logger.info(f"Cloning repository {repo_owner}/{repo_name}.")
        
        # Check if access_token is None and handle accordingly
        github_token = self.access_token if self.access_token else None

        with GitUtils(repo_owner=repo_owner, repo_name=repo_name, base_directory=dir_path, github_token=github_token) as GitInit:
            GitInit.clone_all_branches()
            default_branch = GitInit.get_default_branch()
            all_branches = GitInit.get_github_branches()
        
        self.logger.info(f"Cloning repository {repo_owner}/{repo_name} [done]")
        return default_branch, all_branches

    def add_repository_to_db(self, default_branch, dir_path):
        repo = GitRepository(repo_url=self.proj_url,privacy=self.privacy, access_token=self.access_token, default_branch=default_branch, project_id=self.task_id, path_=dir_path)
        # try:
        with db.session.begin_nested():
            db.session.add(repo)
        db.session.commit()
        self.logger.info(f"Repository {self.proj_url} added to the database. [done]")
        return repo
        # except IntegrityError:
        #     db.session.rollback()
        #     self.logger.warning(f"Repository {self.proj_url} already exists in the database. [failed]")
        #     return None

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_2_database(self, user,privacy, proj_name, proj_url, description=None, access_token=None):
    task_id = celery.current_task.request.id
    
    logger_setup = LoggerSetup(task_id, proj_name, user)
    __, log_file_path = logger_setup.get_logger()

    _ = DatabaseManager.add_project(task_id, user, proj_name, description)
    project_log = DatabaseManager.add_project_log(task_id, log_file_path)

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
            cloning(task_id, all_branches, repo.id, logger)
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
