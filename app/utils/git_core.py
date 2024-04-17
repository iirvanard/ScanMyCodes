from git import Repo, GitCommandError
import os


class Cloner:

    def __init__(self, repo_url, repo_dir, token=None):
        self.repo_url = repo_url
        self.repo_dir = repo_dir
        self.token = token

        # Disable prompts
        os.environ['GIT_TERMINAL_PROMPT'] = '0'

    def clone_repository(self):
        try:
            # Clone the repository with progress
            if not os.path.exists(self.repo_dir):
                if self.token is None:
                    env_vars = None
                else:
                    env_vars = {
                        "GIT_ASKPASS": "echo",
                        "GIT_USERNAME": "token",
                        "GIT_PASSWORD": self.token
                    }

                Repo.clone_from(self.repo_url,
                                self.repo_dir,
                                depth=1,
                                env=env_vars)
                print("berhasil di clone.")
            else:
                print("Repository already exists.")
                repo = Repo(self.repo_dir)
                origin = repo.remote(name='origin')
                origin.pull()
                print("Repository pulled successfully.")

        except GitCommandError as e:
            if '403' in str(e):
                print(
                    "Error: Authentication failed. Please check your GitHub personal access token."
                )
            else:
                print("An error occurred:", e)


if __name__ == "__main__":
    repo_url = "git@github.com:irvan91110/vito.git"
    repo_dir = "d:/aw"
    token = "asda"

    cloner = Cloner(repo_url, repo_dir, token)
    cloner.clone_repository()
