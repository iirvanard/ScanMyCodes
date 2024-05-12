import os
import uuid
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app import celery, app
from app.extensions import db
from app.models import Project, AnalyzeIssue, GitBranch
from app.models.git_repository import GitRepository
from app.utils.git_core import GitUtils
from app.utils.utils import run_wsl_command, split_url


@celery.task(bind=True,
             autoretry_for=(Exception, ),
             retry_kwargs={'max_retries': 3})
def add_2_database(self,
                   user,
                   proj_name,
                   proj_url,
                   description=None,
                   access_token=None):
    task_id = celery.current_task.request.id
    project_model = Project(project_id=task_id,
                            username=user,
                            project_name=proj_name,
                            description=description)

    try:
        with db.session.begin_nested():
            db.session.add(project_model)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        project_model = Project.query.filter_by(project_id=task_id).first()

    try:
        dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "repository",
                                uuid.UUID(str(task_id)).hex)
        repo_owner, repo_name = split_url(proj_url)
        print(repo_owner, repo_name)
        with GitUtils(repo_owner=repo_owner,
                      repo_name=repo_name,
                      base_directory=dir_path) as GitInit:
            GitInit.clone_all_branches()
            default_branch = GitInit.get_default_branch()
            all_branches = GitInit.get_github_branches()
            project_model.fetched_at = datetime.utcnow()
            project_model.fetch_status = 'success'
            db.session.commit()

        repo = add_to_database_repository(task_id, proj_url, default_branch,
                                          dir_path, access_token)
        cloning(task_id, all_branches, repo.id)
        scanning(task_id, all_branches, dir_path)

        project_model.analyze_status = 'success'
        project_model.analyze_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        project_model.analyze_status = 'failed'
        db.session.rollback()
        # Log the error
        print(f"An error occurred: {e}")

    return "Selesai"


def add_to_database_repository(task_id,
                               proj_url,
                               default_branch,
                               dir_path,
                               access_token=None):
    repo = GitRepository(repo_url=proj_url,
                         access_token=access_token,
                         default_branch=default_branch,
                         project_id=task_id,
                         path_=dir_path)
    try:
        with db.session.begin_nested():
            db.session.add(repo)
        db.session.commit()
        return repo
    except IntegrityError:
        db.session.rollback()
        return None


def cloning(task_id, all_branches, repo_id):
    try:
        with db.session.begin_nested():
            for branch_name in all_branches:
                branch = GitBranch(remote=branch_name,
                                   project_id=task_id,
                                   git_repository_id=repo_id)
                db.session.add(branch)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log the error
        print(f"Error: {e}")


def scanning(task_id, all_branches, dir_path):
    try:
        with db.session.begin_nested():
            for branch_name in all_branches:
                filename = f"{uuid.UUID(str(task_id)).hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{branch_name}.json"
                dir_destination = os.path.join(app.config['STATIC_FOLDER_1'],
                                               "scan", filename)
                dir_source = os.path.join(dir_path, branch_name)

                # Check if the issue already exists
                existing_issue = AnalyzeIssue.query.filter_by(
                    project_id=task_id, branch=branch_name).first()
                if existing_issue:
                    # Update the existing issue
                    existing_issue.path_ = dir_destination
                else:
                    # Create a new issue
                    issue = AnalyzeIssue(project_id=task_id,
                                         path_=dir_destination,
                                         branch=branch_name)
                    db.session.add(issue)

                run_wsl_command(dir_source, dir_destination)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log the error
        print(f"Error: {e}")
