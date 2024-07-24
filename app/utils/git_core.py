import os
import requests
import logging
from git import Repo, GitCommandError
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
        self.base_directory = base_directory
        self.github_token = github_token
        self.logger = logging.getLogger(__name__)
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}.git"

        if self.check_repo_privacy() and not self.github_token:
            print()
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
            return True
        else:
            self.logger.error(f"Error: {response.status_code}")
            response.raise_for_status()

    def validate_github_token(self):
        headers = {"Authorization": f"token {self.github_token}"}
        url = f"{self.GITHUB_API_BASE_URL}/user"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return True
    
    def get_github_branches(self):
        headers = {
            "Authorization": f"token {self.github_token}"
        } if self.github_token else {}
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/branches"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        branches_info = response.json()
        branches = {
            branch['name']: branch['commit']['sha']
            for branch in branches_info
        }
        return branches

    def clone_github_branch(self, branch_name):
        clone_dir = os.path.join(self.base_directory, branch_name)

        # Setting http.postBuffer for the repository
    
        try:
            github_url = self.repo_url.replace('https://', f'https://{self.github_token}@')
            Repo.clone_from(github_url,
                            clone_dir,
                            branch=branch_name)
            self.logger.info(
                f"Branch '{branch_name}' was cloned successfully.")
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
        headers = {
            "Authorization": f"token {self.github_token}"
        } if self.github_token else {}
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/commits/{branch}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commit_info = response.json()
        return commit_info['sha']
    
    def get_default_branch(self):
        headers = {
            "Authorization": f"token {self.github_token}"
        } if self.github_token else {}
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repo_info = response.json()
        return repo_info['default_branch']
    

    def get_latest_commit_sha(self, branch):
        try:
            headers = {
                "Authorization": f"token {self.github_token}"
            } if self.github_token else {}
            url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/commits/{branch}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commit_info = response.json()
            return commit_info['sha']

        except requests.exceptions.HTTPError as http_err:
            # You can log the error or perform any other action here before re-raising
            print(f"HTTP error occurred: {http_err}")
            raise  # Re-raise the caught exception
        except Exception as e:
            print(f"Error in async_remote_repo: {e}")
            return "An error occurred during the update check."

    def async_remote_repo(self, branch, local_latest_commits):
        try:
            remote_latest_commits = self.get_latest_commit_sha(branch=branch)
            if remote_latest_commits is None:
                return "Error occurred while fetching remote commit SHA."
            
            # Compare remote commit SHA with local commit SHA
            if remote_latest_commits != local_latest_commits:
                return False
            else:
                return True
            
        except Exception as e:
            print(f"Error in async_remote_repo: {e}")
            return "An error occurred during the update check."