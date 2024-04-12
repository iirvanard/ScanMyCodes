import os
import subprocess


def clone_or_pull(repo_url, destination_path):
    full_path = os.path.join("D:/", destination_path)

    # full_path = os.path.join(os.getcwd(), destination_path)

    if os.path.exists(full_path):
        # If the repository already exists locally, pull changes
        try:
            subprocess.run(['git', 'pull'], cwd=full_path, check=True)
            print("Pull successful")
        except subprocess.CalledProcessError:
            print("Failed to pull changes")
    else:
        # If the repository doesn't exist locally, clone it
        try:
            subprocess.run(['git', 'clone', repo_url, full_path], check=True)
            print("Clone successful")
        except subprocess.CalledProcessError:
            print("Failed to clone repository")


# Example usage:
repo_url = "https://github.com/irvan91110/tugas_akhir.git"
relative_path = "path"
clone_or_pull(repo_url, relative_path)
