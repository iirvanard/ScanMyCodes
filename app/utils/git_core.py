import os
import requests
import logging
from git import Repo, GitCommandError, Git
import shutil

# Set up logging
logging.basicConfig(level=logging.DEBUG)


class GitUtils:
    GITHUB_API_BASE_URL = "https://api.github.com"

    def __init__(self,
                 repo_owner,
                 repo_name,
                 base_directory=None,
                 github_token=None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_directory = base_directory or os.getcwd()  # Default to current directory if None
        self.github_token = github_token
        self.logger = logging.getLogger(__name__)
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}.git"

        if self.check_repo_privacy() and not self.github_token:
            raise ValueError("Access token required for private repository.")

        if self.github_token:
            if not self.validate_github_token():
                raise ValueError("Invalid GitHub token provided.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def check_repo_privacy(self):
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            repo_info = response.json()
            return repo_info.get('private', False)
        elif response.status_code == 404:
            self.logger.error(f"Repository '{self.repo_owner}/{self.repo_name}' not found.")
            return False  # Assume repository is public if not found
        else:
            self.logger.error(f"Error checking repository privacy: {response.status_code}")
            response.raise_for_status()

    def validate_github_token(self):
        headers = {"Authorization": f"token {self.github_token}"}
        url = f"{self.GITHUB_API_BASE_URL}/user"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return True
    
    def get_github_branches(self):
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/branches"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        branches_info = response.json()
        return {branch['name']: branch['commit']['sha'] for branch in branches_info}

    def clone_github_branch(self, branch_name):
        if not self.base_directory:
            raise ValueError("Base directory is not set.")

        clone_dir = os.path.join(self.base_directory, branch_name)

        # Setting http.postBuffer for the repository
        git = Git()
        git.config('http.lowSpeedLimit', '0')
        git.config('http.lowSpeedTime', '999999')
        git.config('http.postBuffer', '1048576000')  # 500 MB buffer size

        try:
            github_url = self.repo_url.replace('https://', f'https://{self.github_token}@')
            Repo.clone_from(github_url, clone_dir, branch=branch_name, depth=1)
            self.logger.info(f"Branch '{branch_name}' was cloned successfully.")
        except GitCommandError as e:
            self.logger.error(f"Failed to clone branch '{branch_name}': {e}")
            raise ValueError(f"Failed to clone branch '{branch_name}': {e}")

        return clone_dir

    def clone_all_branches(self):
        try:
            branches = self.get_github_branches()
            self.logger.info("Branches:")
            for branch, commit_sha in branches.items():
                self.logger.info(f"Cloning branch '{branch}'...")
                self.clone_github_branch(branch)
            self.logger.info("All branches cloned successfully.")
        except Exception as e:
            self.logger.error(f"An error occurred while cloning branches: {e}")
            raise ValueError(f"An error occurred while cloning branches: {e}")

    def get_latest_commit_sha(self, branch):
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/commits/{branch}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commit_info = response.json()
        return commit_info['sha']
    
    def get_default_branch(self):
        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repo_info = response.json()
        return repo_info['default_branch']

    def async_remote_repo(self, branch, local_latest_commits):
        try:
            remote_latest_commit_sha = self.get_latest_commit_sha(branch=branch)
            if remote_latest_commit_sha is None:
                self.logger.error(f"Error occurred while fetching remote commit SHA for branch '{branch}'.")
                return False  # Indicate failure to fetch commit SHA
            
            # Compare remote commit SHA with local commit SHA
            return remote_latest_commit_sha != local_latest_commits
        except Exception as e:
            self.logger.error(f"Error in async_remote_repo: {e}")
            return False  # Indicate an error occurred
