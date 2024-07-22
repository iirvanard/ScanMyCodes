
from app.extensions import db
from app.utils.utils import run_wsl_command
import uuid
from datetime import datetime
import os
from app.models import GitRepository,OpenaiProject
from app import celery, app

@celery.task()
def update_project_task(project_id, requests):
    repository = GitRepository.query.filter_by(project_id=project_id).first()
    openai = OpenaiProject.query.filter_by(project_id=project_id).first()
    
    if (requests.get("privacy")):
        repository.privacy = not repository.privacy

    if (requests.get("personal_token")):
        if (repository.privacy):
            repository.access_token = requests.get("personal_token")
        else:
            return "privacy need to be private to set access token"
        

    # Dapatkan data dari request
    openai_forms = requests.get("openai_forms")

    # Pastikan openai_forms bukan None dan memiliki nilai yang benar
    if openai_forms:
        # Periksa apakah openai_forms adalah "pai-001"
        if openai_forms == "pai-001":
            new_model = "pai-001"
            new_key = "pk-UUyyKsstUMevQnTCDZekLRoTZwJDyajkvVGiXWQJvIyrpOLB"
            new_url = "https://api.pawan.krd/v1/"
        else:
            new_model = requests.get("openai_model")
            new_key = requests.get("openai_token")
            new_url =requests.get("openai_url")

        # Cek apakah data baru berbeda dari data yang ada
        if (openai.openai_model != new_model or
            openai.openai_key != new_key or
            openai.openai_url != new_url):
            
            # Update informasi yang ada jika data baru berbeda
            openai.openai_model = new_model
            openai.openai_key = new_key
            openai.openai_url = new_url
            
            

    db.session.commit()

    return ""