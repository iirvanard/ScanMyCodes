import os
import uuid
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import celery, app
from app.extensions import db
from app.models import Project, AnalyzeIssue, GitBranch, ProjectLog
from app.models.git_repository import GitRepository
from app.utils.git_core import GitUtils
from app.utils.utils import run_wsl_command, split_url

class GitError(Exception):
    def __init__(self, message):
        self.message = message

class LoggerSetup:
    def __init__(self, task_id, proj_name, user):
        self.task_id = task_id
        self.proj_name = proj_name
        self.user = user
        self.logger = logging.getLogger(task_id)
        self.log_file_path = None
        self.setup_logger()

    def setup_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        self.logger.setLevel(logging.INFO)

        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log")
        os.makedirs(dir_path, exist_ok=True)
        
        self.log_file_path = os.path.join(dir_path, f"{uuid.uuid4().hex}.log")
        
        fh = logging.FileHandler(self.log_file_path)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        self.logger.info(f"Task {self.task_id} started for project {self.proj_name} by user {self.user}.  [done]")

    def get_logger(self):
        return self.logger, self.log_file_path

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
    def __init__(self, task_id, proj_url, logger,access_token=None):
        self.task_id = task_id
        self.proj_url = proj_url
        self.logger = logger
        self.access_token = access_token

    def clone_repository(self, dir_path):
        repo_owner, repo_name = split_url(self.proj_url)
        self.logger.info(f"Cloning repository {repo_owner}/{repo_name}.  [done]")
        with GitUtils(repo_owner=repo_owner, repo_name=repo_name, base_directory=dir_path,github_token=self.access_token) as GitInit:
            GitInit.clone_all_branches()
            default_branch = GitInit.get_default_branch()
            all_branches = GitInit.get_github_branches()
        return default_branch, all_branches

    def add_repository_to_db(self, default_branch, dir_path):
        repo = GitRepository(repo_url=self.proj_url, access_token=self.access_token, default_branch=default_branch, project_id=self.task_id, path_=dir_path)
        try:
            with db.session.begin_nested():
                db.session.add(repo)
            db.session.commit()
            self.logger.info(f"Repository {self.proj_url} added to the database. [done]")
            return repo
        except IntegrityError:
            db.session.rollback()
            self.logger.warning(f"Repository {self.proj_url} already exists in the database. [failed]")
            return None

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_2_database(self, user, proj_name, proj_url, description=None, access_token=None):
    task_id = celery.current_task.request.id
    
    logger_setup = LoggerSetup(task_id, proj_name, user)
    logger, log_file_path = logger_setup.get_logger()

    project_model = DatabaseManager.add_project(task_id, user, proj_name, description)
    project_log = DatabaseManager.add_project_log(task_id, log_file_path)

    return add.delay(task_id, proj_url, project_log.id, proj_name, access_token)

@celery.task()
def add(task_id, proj_url, log_id, proj_name, access_token=None):
    try:
        project_log = ProjectLog.query.filter_by(id=log_id).first()

        logger = logging.getLogger(task_id)
        if not logger.handlers:
            fh = logging.FileHandler(project_log.path_)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)
    
        project_model = Project.query.filter_by(project_id=task_id).first()
        if not project_model:
            logger.error(f"Project with task ID {task_id} not found in the database.  [failed]")
            return
        
        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "repository", uuid.UUID(task_id).hex)
        git_handler = GitHandler(task_id, proj_url, logger,access_token=access_token)
        default_branch, all_branches = git_handler.clone_repository(dir_path,access_token=access_token)

        project_model.fetched_at = datetime.now()
        project_model.fetch_status = 'success'
        db.session.commit()

        repo = git_handler.add_repository_to_db(default_branch, dir_path, access_token)
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

def cloning(task_id, all_branches, repo_id, logger):
    try:
        with db.session.begin_nested():
            for branch_name in all_branches:
                branch = GitBranch(remote=branch_name, project_id=task_id, git_repository_id=repo_id)
                db.session.add(branch)
        db.session.commit()
        logger.info(f"All branches for task {task_id} cloned successfully. [done]")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during cloning branches for task {task_id}: {e}. [failed]")

def scanning(task_id, all_branches, dir_path, logger):
    try:
        with db.session.begin_nested():
            for branch_name in all_branches:
                filename = f"{uuid.UUID(task_id).hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{branch_name}.json"
                dir_destination = os.path.join(app.config['STATIC_FOLDER_1'], "scan", filename)
                dir_source = os.path.join(dir_path, branch_name)

                existing_issue = AnalyzeIssue.query.filter_by(project_id=task_id, branch=branch_name).first()
                if existing_issue:
                    existing_issue.path_ = dir_destination
                else:
                    issue = AnalyzeIssue(project_id=task_id, path_=dir_destination, branch=branch_name)
                    db.session.add(issue)

                run_wsl_command(dir_source, dir_destination)

        db.session.commit()
        logger.info(f"Scanning of branches for task {task_id} completed successfully. [done]")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during scanning branches for task {task_id}: {e}. [failed]")
