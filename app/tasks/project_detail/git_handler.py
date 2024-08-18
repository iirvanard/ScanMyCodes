import os
import shutil
import uuid

import requests
from app.models import GitRepository,AnalyzeIssue
from app.models.git_branch import GitBranch
from .scanning_project import scanning
from app.utils.git_core import GitUtils
from app.utils.utils import split_url
from app.extensions import db,SQLAlchemyError
from app import app

class GitHandler:
    def __init__(self, task_id, proj_url=None, logger=None, privacy=None, access_token=None):
        self.task_id = task_id
        self.proj_url = proj_url
        self.logger = logger
        self.privacy = privacy
        self.access_token = access_token

    def clone_repository(self, dir_path):
        repo_owner, repo_name = split_url(self.proj_url)
        self.logger.info(f"Cloning repository {repo_owner}/{repo_name}.")
        
        github_token = self.access_token if self.access_token else None

        with GitUtils(repo_owner=repo_owner, repo_name=repo_name, base_directory=dir_path, github_token=github_token) as git_init:
            git_init.clone_all_branches()
            default_branch = git_init.get_default_branch()
            all_branches = git_init.get_github_branches()
        
        self.logger.info(f"Cloning repository {repo_owner}/{repo_name} [done]")
        return default_branch, all_branches

    def add_repository_to_db(self, default_branch, dir_path):
        repo = GitRepository(
            repo_url=self.proj_url,
            privacy=self.privacy,
            access_token=self.access_token,
            default_branch=default_branch,
            project_id=self.task_id,
        )
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



    def check_for_update(self):
        self.logger.info("Starting update check process.")
        
        branches = GitBranch.query.filter_by(project_id=self.task_id).all()
        self.logger.info(f"Found {len(branches)} branches for project ID {self.task_id}.")
        
        directory = os.path.join(app.config['STATIC_FOLDER_1'], "repository", self.task_id)
        
        repo_owner, repo_name = split_url(self.proj_url)
        
        github_token = self.access_token if self.access_token else None
        git_utils = GitUtils(repo_owner=repo_owner, repo_name=repo_name, github_token=github_token, base_directory=directory)
        self.logger.info("GitUtils initialized.")

        for branch in branches:
            self.logger.info(f"Processing branch: {branch.remote}")
            
            try:
                # Check if remote repository is up-to-date
                is_up_to_date = git_utils.async_remote_repo(branch=branch.remote, local_latest_commits=branch.latest_commits)
                self.logger.info(f"Branch {branch.remote} up-to-date status: {is_up_to_date}.")
                
                if not is_up_to_date:
                    latest_commit = git_utils.get_latest_commit_sha(branch=branch.remote)
                    self.logger.info(f"Branch {branch.remote} has a new commit: {latest_commit}.")
                    
                    branch.latest_commits = latest_commit
                    self.logger.info(f"Updated branch {branch.remote} latest commits in database.")

                    self.logger.info(f"Cloning repository {repo_owner}/{repo_name} branch {branch.remote}.")
                    try:
                        git_utils.clone_github_branch(branch.remote)
                        self.logger.info(f"Successfully cloned branch {branch.remote}.")
                        
                        analyze = AnalyzeIssue.query.filter_by(project_id=self.task_id, branch=branch.id).all()
                        self.logger.info(f"Found {len(analyze)} analysis issues for branch {branch.remote}.")
                        
                        for analysis in analyze:
                            self.logger.info(f"Running scanning on {analysis.path_}.")
                            scanning(task_id=self.task_id, all_branches=[branch.remote], dir_path=directory, filename=analysis.path_, logger=self.logger)
                        
                    except Exception as clone_err:
                        self.logger.error(f"Error cloning branch {branch.remote}: {clone_err}")
                        shutil.rmtree(directory)
                        self.logger.info(f"Removed directory {directory} due to cloning error.")
                    
                    db.session.commit()
                    self.logger.info(f"Database commit successful after processing branch {branch.remote}.")

            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 404:
                    self.logger.warning(f"Branch {branch.remote} not found on remote. Deleting from local database.")
                    db.session.delete(branch)
                    db.session.commit()
                    self.logger.info(f"Branch {branch.remote} deleted from database.")
                else:
                    self.logger.error(f"HTTP error occurred: {http_err}")
                    raise

            except Exception as e:
                db.session.rollback()
                self.logger.error(f"Unexpected error occurred: {e}")
                return f"An error occurred during the update check: {e}"

        self.logger.info("Update check process completed.")