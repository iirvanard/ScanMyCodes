
from app.extensions import db
from app.utils.utils import run_wsl_command
import uuid
from datetime import datetime
import os
from app.models import  AnalyzeIssue
from app import app

def scanning(task_id, all_branches, dir_path, logger,filename=None):
    try:
        with db.session.begin_nested():
            for branch_name in all_branches:
                if (filename is None):
                    filename = f"{uuid.UUID(task_id).hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{branch_name}.json"
                
                dir_destination = os.path.join(app.config['STATIC_FOLDER_1'], "scan", filename)
                dir_source = os.path.join(dir_path, branch_name)

                existing_issue = AnalyzeIssue.query.filter_by(project_id=task_id, branch=branch_name).first()
                if existing_issue:
                    existing_issue.path_ = dir_destination
                else:
                    issue = AnalyzeIssue(project_id=task_id, path_=filename, branch=branch_name)
                    db.session.add(issue)

                run_wsl_command(dir_source, dir_destination)

        db.session.commit()
        logger.info(f"Scanning of branches for task {task_id} completed successfully. [done]")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during scanning branches for task {task_id}: {e}. [failed]")