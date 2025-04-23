import os
import uuid
import logging
from app import celery, app
from app.extensions import db
from app.models import Project, AnalyzeIssue, GitBranch, ProjectLog,OpenaiProject
from app.models.git_repository import GitRepository
import shutil

@celery.task()
def delete_project_task(project_id):
    logger = logging.getLogger(f"delete_project_{project_id}")
    logger.setLevel(logging.INFO)
    logger.info(f"Starting deletion of project {project_id}.")

    try:
        project_analyze= AnalyzeIssue.query.filter_by(project_id=project_id).all()

        # Loop through the results
        for analyze in project_analyze:

            logger.info("1")
            # Build the full path to the project file
            project_file = os.path.join(app.config['STATIC_FOLDER_1'], "scan", analyze.path_)

            # Attempt to remove the file
            try:
                os.remove(project_file)
                logger.info(f"File removed: {project_file}")
            except FileNotFoundError:
                logger.info(f"File does not exist: {project_file}")
            except Exception as e:
                logger.error(f"Error removing file {project_file}: {e}")

        # Delete openai_project
        OpenaiProject.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        logger.info(f"Deleted analyze issues for project {project_id}.")
        
        # Delete AnalyzeIssues
        AnalyzeIssue.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        logger.info(f"Deleted analyze issues for project {project_id}.")
        

        # Delete GitBranches
        GitBranch.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        logger.info(f"Deleted git branches for project {project_id}.")

        # Delete GitRepository
        GitRepository.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        logger.info(f"Deleted git repository for project {project_id}.")
        # Query to get all ProjectLog entries for the given project_id
        project_logs = ProjectLog.query.filter_by(project_id=project_id).all()


        # Loop through the results
        for log in project_logs:
            # Build the full path to the project file
            project_file = os.path.join(app.config['STATIC_FOLDER_1'], "log", log.path_)

            # Attempt to remove the file
            try:
                os.remove(project_file)
                logger.info(f"File removed: {project_file}")
            except FileNotFoundError:
                logger.info(f"File does not exist: {project_file}")
            except Exception as e:
                logger.error(f"Error removing file {project_file}: {e}")

        # Delete ProjectLogs in a single batch
        ProjectLog.query.filter_by(project_id=project_id).delete(synchronize_session=False)
        db.session.commit()
        logger.info(f"Deleted project logs for project {project_id}.")

        # Delete Project
        Project.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        logger.info(f"Deleted project {project_id} from database.")

        # Remove project files
        project_dir = os.path.join(app.config['STATIC_FOLDER_1'], "repository", uuid.UUID(project_id).hex)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
            logger.info(f"Deleted project directory {project_dir}.")

        logger.info(f"Project {project_id} deletion completed successfully.")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during deletion of project {project_id}: {e}.")
        raise e

    return "Project deletion completed."
