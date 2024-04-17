from flask import Blueprint, jsonify, flash, redirect, render_template, url_for, request
from datetime import datetime
from app.models.project import Project
from app.extensions import login_user, logout_user, login_required

blueprint = Blueprint('project', __name__, url_prefix='/project')

# @blueprint.route("/", methods=["GET"])
# def index():
#     projects = Project.query.all()
#     serialized_projects = []

#     for project in projects:
#         serialized_project = {
#             'id': project.id,
#             'username': project.username,
#             'git_urls': project.git_urls,
#             'last_update': project.last_update,
#             'created_at': project.created_at,
#         }
#         serialized_projects.append(serialized_project)


@blueprint.route("/", methods=["GET"])
def index():
    # users = User.query.all()
    # serialized_users = []

    # for user in users:
    #     serialized_user = {
    #         'id': user.id,
    #         'username': user.username,
    #     }
    #     serialized_users.append(serialized_user)

    return redirect(url_for('project.analysis'))


@blueprint.route("/analysis", methods=["GET"])
def analysis():
    # users = User.query.all()
    # serialized_users = []

    # for user in users:
    #     serialized_user = {
    #         'id': user.id,
    #         'username': user.username,
    #     }
    #     serialized_users.append(serialized_user)

    return render_template("/project/analysis/index.html",
                           title="project title")


@blueprint.route("/analysis/<string:branchid>", methods=["GET"])
def analysisByBranch(branchid):
    analysis_content = branchid

    return render_template('/project/analysis/index.html',
                           analysis_content=analysis_content,
                           BranchName=branchid,
                           title="branch dev")


@blueprint.route('/log')
def log():
    return render_template('/project/log/log.html', title="log - 12313123")


@blueprint.route('/log/<string:logId>')
def LogById(logId):

    return render_template('/project/log/log_item.html',
                           id=logId,
                           title="log details - 123123")


@blueprint.route('/contact')
def contact():
    return render_template('/project/analysis/contact.html')


# @blueprint.route("/", methods=["GET"])
# @login_required
# def index():
#     projects = Project.query.all()
#     serialized_projects = []

#     for project in projects:
#         serialized_project = {
#             'id': project.id,
#             'username': project.username,
#             'git_urls': project.git_urls,
#             'last_update': project.last_update,
#             'created_at': project.created_at,
#         }
#         serialized_projects.append(serialized_project)

#     return jsonify(serialized_projects)

# @blueprint.route('/add_project', methods=['POST'])
# @login_required
# def add_project():
#     try:
#         form = request.form
#         if form.get('email') and form.get('username'):
#             email = form.get('email')
#             username = form.get('username')
#             if Project.query.filter_by(
#                     email=email).first() or Project.query.filter_by(
#                         username=username).first():
#                 flash('Email or username already registered', 'error')
#                 return redirect(url_for('auth.auth', _anchor='register'))
#             # Define hashed_password if it's not defined elsewhere
#             Project.insert_project(username=form.get('username'),
#                                    git_urls=form.get('git_urls'),
#                                    last_update=datetime.now(),
#                                    created_at=datetime.now())
#             flash('Registration successful. You can now login.', 'success')
#             return redirect(url_for('auth.auth'))
#         else:
#             flash('Registration failed. Please check your input.', 'error')
#             return redirect(url_for('auth.auth', _anchor='register'))
#     except Exception as e:
#         flash('An error occurred. Please try again later.', 'error')
#         print(e)
#         return redirect(url_for('index.index'))
