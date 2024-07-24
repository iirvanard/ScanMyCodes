
from app.extensions import db
from app.models import GitBranch

def addGitBranch(task_id, all_branches, repo_id, logger):
    try:
        with db.session.begin_nested():
            for branch_name, sha in all_branches.items():
                branch = GitBranch(remote=branch_name, latest_commits=sha,project_id=task_id, git_repository_id=repo_id)
                db.session.add(branch)
        db.session.commit()
        logger.info(f"All branches for task {task_id} cloned successfully. [done]")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during cloning branches for task {task_id}: {e}. [failed]")
