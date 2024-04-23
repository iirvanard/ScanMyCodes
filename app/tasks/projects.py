from app import celery
from app.extensions import db

from app.models.project import Project  
from app.models.git_repository import GitRepository  
from celery import chain
import paramiko

# Create Celery instance


# Define and register task
@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_2_database(self, user, proj_name, proj_url, description=None):


    project_model = Project(username=user, project_name=proj_name, description=description) 
    db.session.add(project_model)
    db.session.commit()
    res = chain(add_git_repository.s(project_model.project_id, proj_url))()
    return res


# Define and register task
@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def add_git_repository(self, project_id, proj_url):
    # project = Project.query.get(project_id)
   
    key = paramiko.RSAKey.generate(bits=2048)
    public_key_string = f"{key.get_name()} {key.get_base64()}"
    
    repo = GitRepository(public_key=public_key_string,repo_url=proj_url,default_branch="origin/main",project_id=project_id,path_="testpath")
    
    db.session.add(repo)
    db.session.commit()
    # You can add your logic to interact with Git here
    return "test"
