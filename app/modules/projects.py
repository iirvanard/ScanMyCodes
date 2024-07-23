from flask import Blueprint, redirect, request, render_template, url_for
from app.models.project import Project
from flask_login import current_user
from app.tasks.project_detail.add_project import add_2_database  # Import Celery task
import uuid
from flask_login import login_required
from celery.result import AsyncResult
from app import celery
import time

blueprint = Blueprint('projects', __name__, url_prefix='/project')


@blueprint.route("/", methods=["GET"])
@login_required
def index():

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()

    query = Project.query.filter(Project.username == current_user.username)

    # Sorting projects by creation date in descending order
    query = query.order_by(Project.created_at.desc())
    
    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Project.project_name.ilike(f'%{term}%'))

    projects_pagination = query.paginate(page=page,
                                         per_page=10,
                                         error_out=False)
    projects = projects_pagination.items

    return render_template("projects/index.html",
                           proj_list=projects,
                           pagination=projects_pagination,
                           search=search)


@blueprint.route("/add", methods=["POST"])
@login_required
def add():
    project_name = request.form.get('projectName')
    project_url = request.form.get('projectURL')
    description = request.form.get('description')
    access_token = request.form.get('personal_token') or None
    privacy = request.form.get('privacy') is not None

    result = add_2_database.delay(user=current_user.username,privacy=privacy, proj_name=project_name,proj_url=project_url, description=description, access_token=access_token)
    
    # Menunggu sampai tugas selesai
    task_result = AsyncResult(result.id, app=celery)
    while not task_result.ready():
        time.sleep(1)
    
    
    return redirect(url_for('projects.index') + str(result.id))

