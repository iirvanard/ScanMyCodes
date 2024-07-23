
from app.extensions import db

from app.models import GitRepository,OpenaiProject,Project
from app import celery
@celery.task()
def update_project_task(project_id, requests):
    repository = GitRepository.query.filter_by(project_id=project_id).first()
    openai = OpenaiProject.query.filter_by(project_id=project_id).first()
    project = Project.query.filter_by(project_id=project_id).first()

    if project is not None:
        project_name = requests.get('projectName')
        if project_name and project_name != project.project_name:
            project.project_name = project_name

        project_url = requests.get('projectUrl')
        if project_url and project_url != repository.repo_url:
            repository.repo_url = project_url

        description = requests.get('description')
        if description and description != project.description:
            project.description = description

    if (requests.get("privacy")):
        repository.privacy = not repository.privacy
    
    personal_token = requests.get('personal_token')
    # Periksa dan update access_token jika repository privacy dan personal_token berbeda
    if personal_token:
        if repository.privacy:
            if personal_token != repository.access_token:
                repository.access_token = personal_token
        else:
            return "Privacy needs to be set to private to set access token"
    

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