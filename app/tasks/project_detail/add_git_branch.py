from app.extensions import db
from app.models import GitBranch
import os

def addGitBranch(task_id, all_branches, repo_id, logger):
    try:
        with db.session.begin_nested():
            for branch_name, sha in all_branches.items():
                # Menggunakan os.path.basename untuk mendapatkan bagian setelah '/'
                branch_name = os.path.basename(branch_name)

                # Menambahkan branch ke database
                branch = GitBranch(remote=branch_name, latest_commits=sha, project_id=task_id, git_repository_id=repo_id)
                db.session.add(branch)

        # Commit perubahan ke database
        db.session.commit()
        logger.info(f"All branches for task {task_id} cloned successfully. [done]")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during cloning branches for task {task_id}: {e}. [failed]")
