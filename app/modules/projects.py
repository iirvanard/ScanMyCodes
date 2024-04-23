from flask import Blueprint, abort, jsonify, flash, redirect,request, render_template, url_for
from app.models.project import Project,db
from flask_login import current_user
from app.tasks.projects import add_2_database # Import Celery task
from celery.result import AsyncResult


blueprint = Blueprint('projects',
                      __name__,
                      url_prefix='/project')


@blueprint.route("/", methods=["GET"])
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    query = Project.query.filter(Project.username == current_user.username)
    if search:
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(Project.project_name.ilike(f'%{term}%'))
    projects_pagination = query.paginate(page=page, per_page=10, error_out=False)
    projects = projects_pagination.items
  
    for project in projects:
        project.project_id = project.project_id.hex
        
    return render_template("projects/index.html", proj_list=projects, pagination=projects_pagination, search=search)



@blueprint.route("/add", methods=["POST"])
def add():
    project_name = request.form.get('projectName')
    project_url = request.form.get('projectURL')
    description = request.form.get('description')
    result = add_2_database.delay(current_user.username,project_name,project_url,description)
    return str(result)
    # return redirect(url_for("projects.index"))



@blueprint.route("/ese", methods=["GET"])
def ese():
    task_result = AsyncResult('f905b62e-fb2c-43d5-aa23-c42d2dfb120e')

    print(task_result)
    return str(task_result.date_done)





@blueprint.route("/update", methods=["POST"])
def update():
    return "update"