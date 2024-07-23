from app.extensions import db
from app.models import GitRepository, OpenaiProject, Project
from app import celery
from .git_handler import GitHandler
from .scanning_project import scanning
from .logger import LoggerSetup
import logging

@celery.task()
def checkRemote(id_project):
    try:

        repository = GitRepository.query.filter_by(project_id=id_project).first()

        git_handler = GitHandler(task_id=id_project,proj_url=repository.repo_url,access_token=repository.access_token)
        git_handler.git_pull(repository.path_)
        
        logger = logging.getLogger(id_project)
        if not logger.handlers:
            fh = logging.FileHandler('1740f6c7036a43e18ccadb733173ce9b.log')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)

        scanning(task_id=id_project,all_branches=git_handler.all_branch(basedir=repository.path_),dir_path=repository.path_,logger=logger,filename="c9b48348a57b4b7b9295951f7b75a026_20240723_203010_main.json")

        return "Project {id_project} successfully"
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}"
