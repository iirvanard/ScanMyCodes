from flask import Blueprint, redirect, request, render_template, url_for
from app.models.project import Project
from flask_login import current_user
from app.tasks.projects import add_2_database  # Import Celery task
import uuid
from flask_login import login_required

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

    for project in projects:
        project.project_id = project.project_id.hex

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
    access_token = request.form.get('accessToken')  # Diambil dari form
    result = add_2_database.delay(current_user.username, project_name,
                                  project_url, description, access_token)
    hex_result = uuid.UUID(str(result)).hex  # Convert UUID to hexadecimal
    return redirect(url_for('projects.index') + str(hex_result))


@blueprint.route("/update", methods=["POST"])
def update():
    return "update"
