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

formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

def setup_logger(task_id, proj_name, user):
    """Set up logger for the given task."""
    logger = logging.getLogger(task_id)  # Use task_id as logger name to avoid conflicts
    logger.setLevel(logging.INFO)

    dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log")
    os.makedirs(dir_path, exist_ok=True)
    
    log_file_path = os.path.join(dir_path, f"{uuid.uuid4().hex}.log")
    
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(formatter)  # Apply the global formatter
    logger.addHandler(fh)
    
    logger.info(f"Task {task_id} started for project {proj_name} by user {user}.  [done]")

    return logger, log_file_path

@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_2_database(self, user, proj_name, proj_url, description=None, access_token=None):
    task_id = celery.current_task.request.id
    
    logger, log_file_path = setup_logger(task_id, proj_name, user)

    project_model = Project(project_id=task_id, username=user, project_name=proj_name, description=description)

    try:
        with db.session.begin_nested():
            db.session.add(project_model)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        project_model = Project.query.filter_by(project_id=task_id).first()

    project_log = ProjectLog(project_id=task_id, type="analyze", status="on progress", path_=log_file_path)
    
    with db.session.begin_nested():
        db.session.add(project_log)
    db.session.commit()

    try:
            project_log = ProjectLog.query.filter_by(id=project_log.id).first()

            # Reinitialize logger with the existing log file path
            logger = logging.getLogger(task_id)
            if not logger.handlers:
                fh = logging.FileHandler(project_log.path_)
                fh.setFormatter(formatter)
                logger.addHandler(fh)
                logger.setLevel(logging.INFO)
        
            project_model = Project.query.filter_by(project_id=task_id).first()
            if not project_model:
                logger.error(f"Project with task ID {task_id} not found in the database.  [failed]")
                return
            
            try:
                dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "repository", uuid.UUID(task_id).hex)
                repo_owner, repo_name = split_url(proj_url)
                logger.info(f"Cloning repository {repo_owner}/{repo_name}.  [done]")

                with GitUtils(repo_owner=repo_owner, repo_name=repo_name, base_directory=dir_path) as GitInit:
                    GitInit.clone_all_branches()
                    default_branch = GitInit.get_default_branch()
                    all_branches = GitInit.get_github_branches()
                    project_model.fetched_at = datetime.now()
                    project_model.fetch_status = 'success'
                    db.session.commit()
                            
            except Exception as e:
                project_model.fetch_status = 'failed'
                db.session.commit()
                raise ValueError(e)

            try:
                # Add repository to the database
                repo = add_to_database_repository(task_id, proj_url, default_branch, dir_path, logger, access_token)

                cloning(task_id, all_branches, repo.id, logger)
                # Scan repository for analysis
                scanning(task_id, all_branches, dir_path, logger)

                # Update project status in the database
                project_model.analyze_status = 'success'
                project_log.status = 'success'
                project_model.analyze_at = datetime.now()
                db.session.commit()
                logger.info(f"Project {proj_name} analyzed successfully. [done]")
            
            except Exception as e:
                db.session.rollback()
                raise ValueError(e)
            
    except Exception as e:
        if project_model:
            project_model.analyze_status = 'failed'
        if project_log:
            project_log.status = 'failed'
        db.session.commit()   
        logger.error(f'{e} [failed]')



def add_to_database_repository(task_id, proj_url, default_branch, dir_path, logger, access_token=None):
    repo = GitRepository(repo_url=proj_url, access_token=access_token, default_branch=default_branch, project_id=task_id, path_=dir_path)
    try:
        with db.session.begin_nested():
            db.session.add(repo)
        db.session.commit()
        logger.info(f"Repository {proj_url} added to the database. [done]")
        return repo
    except IntegrityError:
        db.session.rollback()
        logger.warning(f"Repository {proj_url} already exists in the database. [failed]")
        return None

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
