from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Project, ProjectLog,OpenaiProject,GitRepository


class DatabaseManager:
    @staticmethod
    def add_project(task_id, user_id, proj_name, description):
        project_model = Project(project_id=task_id, user_id=user_id, project_name=proj_name, description=description)
        try:
            with db.session.begin_nested():
                db.session.add(project_model)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            project_model = Project.query.filter_by(project_id=task_id).first()
        return project_model

    @staticmethod
    def add_project_log(task_id, log_file_path,log_type,user_id):
        project_log = ProjectLog(project_id=task_id, user_id=user_id,type=log_type, status="on progress", path_=log_file_path)
        with db.session.begin_nested():
            db.session.add(project_log)
        db.session.commit()
        return project_log

    @staticmethod
    def update_project_status(project_model, status, fetched_at=None, analyze_at=None):
        project_model.analyze_status = status
        if fetched_at:
            project_model.fetched_at = fetched_at
        if analyze_at:
            project_model.analyze_at = analyze_at
        db.session.commit()

    @staticmethod
    def add_project_openai(task_id, openai_model,openai_key,openai_url):
        project_openai = OpenaiProject(project_id=task_id, openai_model=openai_model,openai_key=openai_key,openai_url=openai_url)
        with db.session.begin_nested():
            db.session.add(project_openai)
        db.session.commit()
        return project_openai
