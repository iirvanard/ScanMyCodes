from app.models import GitRepository
from app.utils.git_core import GitUtils
from app.utils.utils import split_url
from app.extensions import db

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
