import os
import requests
import logging
from git import Repo, GitCommandError

# Set up logging
logging.basicConfig(level=logging.DEBUG)


class GitUtils:
    GITHUB_API_BASE_URL = "https://api.github.com"

    def __init__(self,
                 repo_owner,
                 repo_name,
                 base_directory,
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

        try:
            Repo.clone_from(self.repo_url,
                            clone_dir,
                            branch=branch_name,
                            depth=1)
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

    def check_for_updates(self, branch):
        try:
            self.logger.info("Checking for updates in local branches:")
            latest_commit_sha = self.get_latest_commit_sha(branch)
            local_commit_sha = self.get_local_commit_sha(branch)
            if latest_commit_sha != local_commit_sha:
                self.logger.info(f"Updates found in branch '{branch}'.")
                self.pull_github_branch(branch)
            else:
                self.logger.info(f"No updates found in branch '{branch}'.")
            self.logger.info("Update check completed.")
        except Exception as e:
            print(str(e))
            self.logger.error(
                f"An error occurred while checking for updates: {e}")
            raise ValueError(
                f"An error occurred while checking for updates: {e}")

    def get_local_branches(self):
        return [
            d for d in os.listdir(self.base_directory)
            if os.path.isdir(os.path.join(self.base_directory, d))
        ]

    def get_local_commit_sha(self, branch):
        repo_dir = os.path.join(self.base_directory, branch)
        repo = Repo(repo_dir)
        return repo.branches[branch].commit.hexsha

    def pull_github_branch(self, branch_name):
        repo_dir = os.path.join(self.base_directory, branch_name)
        try:
            repo = Repo(repo_dir)
            origin = repo.remotes.origin
            origin.pull()
            self.logger.info(
                f"Branch '{branch_name}' was pulled successfully.")
            return True
        except GitCommandError as e:
            self.logger.error(f"Failed to pull branch '{branch_name}': {e}")
            raise ValueError(f"Failed to pull branch '{branch_name}': {e}")

    def get_latest_commit_sha(self, branch):
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/commits/{branch}"
        response = requests.get(url)
        response.raise_for_status()
        commit_info = response.json()
        return commit_info['sha']

    def get_default_branch(self):
        url = f"{self.GITHUB_API_BASE_URL}/repos/{self.repo_owner}/{self.repo_name}"
        response = requests.get(url)
        response.raise_for_status()
        repo_info = response.json()
        return repo_info['default_branch']


# if __name__ == "__main__":
#     # GitHub repository details
#     repo_owner = "irvan91110"
#     repo_name = "tugas_akhir"

#     # GitHub personal access token (optional)
#     github_token = None  # Set to your GitHub personal access token if needed

#     # Directory to clone the repository into
#     base_directory = "D:/gitpythontest"

#     # Create an instance of GitUtils
#     repo_cloner = GitUtils(repo_owner, repo_name, base_directory,
#                                    github_token)

#     # Check for updates in local branches
#     repo_cloner.check_for_updates("main")
