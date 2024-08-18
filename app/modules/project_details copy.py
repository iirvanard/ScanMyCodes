import datetime
from functools import wraps
import os
from flask import Blueprint,flash, abort,g, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.models import Project, GitBranch, GitRepository, OpenaiProject,AnalyzeIssue,ProjectLog,User
from uuid import UUID
from app.models.project_collaborator import ProjectCollaborator
from app.tasks.project_detail import updateProject,delete_project_task,checkRemote
import json

from celery.result import AsyncResult
from app import celery,app
import time
from sqlalchemy import desc
import secrets
from app.extensions import db

blueprint = Blueprint('project',
                      __name__,
                      url_prefix='/project/<string:idproject>')



# Utility Functions
def get_project_from_id(idproject):
    project = Project.query.filter_by(project_id=idproject).first()
    return project


def get_branches(idproject):
    try:
        # Assuming GitBranch is your SQLAlchemy model
        branches = GitBranch.query.filter_by(
            project_id=str(UUID(idproject))).all()
        return branches
    except Exception as e:
        # Log the exception or handle it as per your requirement
        print("An error occurred while fetching branches:", e)
        return None  # or any other appropriate action, such as raising the exception


# Decorators
def check_branch(func):

    @wraps(func)
    def decorated_function(*args, **kwargs):
        branchid = kwargs.get('branchid')
        if not branchid:
            return func(*args, **kwargs)

        branches = get_branches(kwargs.get('idproject'))
        branch_names = [branch.remote for branch in branches]
        if branchid not in branch_names:
            abort(404)
        return func(*args, **kwargs)

    return decorated_function


def marksdown(idproject, branch):
    try:
        print(branch)
        branchx = GitBranch.query.filter_by(project_id=idproject, remote=branch).first()
        filename = AnalyzeIssue.query.filter_by(project_id=idproject, branch=branchx.id).first()

        dir_destination = os.path.join(app.config['STATIC_FOLDER_1'], "scan", filename.path_)
        
        # Check if the file exists and is not empty
        if not os.path.exists(dir_destination) or os.path.getsize(dir_destination) == 0:
            raise FileNotFoundError(f"The file at {dir_destination} is empty or does not exist.")
        
        # Read and parse the JSON file
        with open(dir_destination, encoding='utf-8') as user_file:
            filejson = user_file.read()
            
            # Check if the file content is valid JSON
            if not filejson.strip():
                raise ValueError("The file is empty.")
            
            try:
                data = json.loads(filejson)
            except json.JSONDecodeError:
                raise ValueError("The file contains invalid JSON.")
        
        # Calculate the statistics
        stats = {
            'C': len(data.get('critical', [])),
            'H': len(data.get('high', [])),
            'M': len(data.get('medium', [])),
            'L': len(data.get('low', [])),
            'W': len(data.get('weak', []))
        }

        return stats, data

    except Exception as e:
        print(f"Error: {e}")
        return {'C': 0, 'H': 0, 'M': 0, 'L': 0, 'W': 0}, {}

def get_project_or_404(idproject):
    """Helper function to fetch the project or abort with 404."""
    project = get_project_from_id(idproject)
    if project is None:
        abort(404)
    return project


def check_idproject(func):
    @wraps(func)
    @login_required
    def decorated_function(*args, **kwargs):
        idproject = kwargs.get('idproject')
        if not idproject:
            abort(404)

        try:
            g.project = get_project_or_404(idproject)
            
            if g.project.user_id == current_user.id:
                # User is the owner
                return func(*args, **kwargs)

            g.collaborator = ProjectCollaborator.query.filter_by(
                project_id=idproject, collaborator_id=current_user.id).first()

            if g.collaborator:
                if g.collaborator.status == 'confirmed':
                    # User is a confirmed collaborator
                    return func(*args, **kwargs)
                elif g.collaborator.status == 'pending':
                    # Redirect to manage invitation
                    return redirect(url_for('project.manage_invitation', idproject=g.project.project_id))
            
            # User is neither the owner nor a collaborator
            abort(404)

        except Exception as e:
            print(f"Error: {e}")
            abort(404)

    return decorated_function

def is_project_manager(func):
    @wraps(func)
    @login_required
    def decorated_function(*args, **kwargs):
        idproject = kwargs.get('idproject')
        if not idproject:
            abort(404)

        try:
            project = get_project_or_404(idproject)
            
            if project.user_id == current_user.id:
                # User is the owner
                return func(*args, **kwargs)

            abort(403)

        except Exception as e:
            print(f"Error: {e}")
            abort(404)

    return decorated_function

# Routes
@blueprint.route("/", methods=["GET"])
@check_idproject
def index(idproject):
    project = get_project_from_id(idproject)
    return redirect(url_for('project.analysis', idproject=project.project_id))


@blueprint.route("/member", methods=["POST"])
@check_idproject 
def add_collaborator(idproject):
    collaborator_user = request.form.get('collaborator_user')
    
    # Validate the input data
    if not collaborator_user:
        return jsonify({"error": "Missing collaborator_id"}), 400
    
    # Query the database for the user
    user = User.query.filter(
        (User.username == collaborator_user) | 
        (User.email == collaborator_user)
    ).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    

    # Create a new ProjectCollaborator instance
    new_collaborator = ProjectCollaborator(
        project_id=idproject,
        inviter_id=current_user.id,
        collaborator_id=user.id
    )
    
    # Add the new collaborator to the session
    db.session.add(new_collaborator)
    
    try:
        # Commit the transaction
        db.session.commit()
        return jsonify({"message": "Collaborator added successfully"}), 201
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    




@blueprint.route("/invitations", methods=["POST", "GET"])
@login_required
def manage_invitation(idproject):
    """
    Handles both POST and GET requests for invitations.
    - POST: Confirms an invitation for the current user.
    - GET: Retrieves the status of the invitation for the current user.
    """

    g.project = get_project_from_id(idproject)
    g.collaborator = ProjectCollaborator.query.filter_by(project_id=idproject, collaborator_id=current_user.id).first()

    if g.collaborator.status == "confirmed" or g.project.user_id == current_user.id:
        return redirect(url_for('project.analysis', idproject=idproject))
    elif g.collaborator.status == "rejected":
        abort(404)

    if request.method == "POST":
        # Handle POST request to confirm the invitation
        try:
            invitation = ProjectCollaborator.query.filter_by(
                    collaborator_id=current_user.id, project_id=idproject
                ).first()
                
            if not invitation:
                    return jsonify({"error": "Invitation not found"}), 404

            invitation.confirm()
            db.session.commit()
            return jsonify({"message": "Invitation confirmed successfully"}), 200
        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    elif request.method == "GET":
        # Handle GET request to retrieve the status of the invitation
        return render_template('/project_detail/invitations/invitation_page.html',
                           
                           idproject=idproject,project=g.project,)

@blueprint.route("/analysis", methods=["GET"])
@blueprint.route("/analysis/<string:branchid>", methods=["GET"])
@check_idproject
@check_branch
def analysis(idproject, branchid=None):
    project = get_project_from_id(idproject)
    branch_names = [branch.remote for branch in get_branches(idproject)]

    # Mendapatkan repository Git
    gitrepo = GitRepository.query.filter_by(
        project_id=str(UUID(idproject))).first()

    # Jika tidak ada branch yang ditentukan dan ada default branch, redirect ke default branch
    if project.analyze_status == "success":
        if branch_names is not None and branchid is None:
            if gitrepo.default_branch is not None:
                return redirect(
                    url_for('project.analysis',
                            idproject=project.project_id,
                            branchid=gitrepo.default_branch))

    stats, markdown_content = marksdown(idproject, branchid)

    filterContent = {
            'Severity': {"high","medium","critical","low","weak"},
            'Language': {"python","php","javascript"},
        }

    analysis_content = render_template(
        '/project_detail/analysis/branch.html',
        filterContent =filterContent
        ,
        content=markdown_content) if branchid else None
    title = f"Branch Dev - {project.project_name}" if branchid else f"Analysis - {project.project_name}"

    return render_template('/project_detail/analysis/index.html',
                           analysis_content=analysis_content,
                           BranchName=branchid,
                           stats=stats,
                           branches=branch_names,
                           title=title,
                           project=project)


@blueprint.route('/log', methods=["GET"])
@check_idproject
def log(idproject):
    project = get_project_from_id(idproject)


    if not project:
        abort(404, description="Project not found")

    # Check if the current user is the project manager
    if project.user_id == current_user.id:
        # If the user is the project manager, show all logs
        logs = ProjectLog.query.filter_by(project_id=idproject).order_by(desc(ProjectLog.created_at)).all()
    else:
        # If the user is not the project manager, show only their logs
        logs = ProjectLog.query.filter_by(project_id=idproject, user_id=current_user.id).order_by(desc(ProjectLog.created_at)).all()

    return render_template(
        '/project_detail/log/log.html',
        title=f"log  - {project.project_name}",
        content = logs,
        project=project,
    )


@blueprint.route('/log/<string:logid>')
@check_idproject
def log_by_id(idproject,logid):
    project = get_project_from_id(idproject)
    log = ProjectLog.query.filter_by(id=logid).first()
    dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log")
    log_file_path = os.path.join(dir_path, log.path_)
    try:
        with open(log_file_path, 'r') as file:
            # Read the contents of the file and split into lines
            content = [line.rstrip('\n') for line in file]
    except FileNotFoundError:
        content = ""
    print(content)
    return render_template(
        '/project_detail/log/log_item.html',
        title=f"log details - {project.project_name}",
        project=project,
        content=log,
        logx=content
    )


@blueprint.route('/settings')
@check_idproject
@is_project_manager
def settings(idproject):
    project = get_project_from_id(idproject)
    repo = GitRepository.query.filter_by(project_id=str(UUID(idproject))).first()
    openai_data = OpenaiProject.query.filter_by(project_id=str(UUID(idproject))).first()
    return render_template(
        '/project_detail/settings/index.html',
        project=project,
        repository=repo,
        openai=openai_data
    )



@blueprint.route("/settings/delete", methods=["POST"])
@check_idproject
@is_project_manager
def delete_project(idproject):
    # Start the task
    task = delete_project_task.delay(idproject)
    
    # Poll for task completion
    while True:
        result = AsyncResult(task.id, app=celery)
        if result.state == 'SUCCESS':
            # Task succeeded, redirect
            return redirect(url_for('projects.index'))
        elif result.state == 'FAILURE':
            # Task failed, handle failure
            return jsonify({'error': 'Task failed'}), 500
        else:
            # Task is still pending or in progress, wait a bit and check again
            time.sleep(1)

@blueprint.route("/update", methods=["POST"])
@check_idproject
@is_project_manager
def update_project(idproject):
    # Start the task
    task = updateProject.delay(project_id=idproject,requests=(request.form))

    # Poll for task completion
    while True:
        result = AsyncResult(task.id, app=celery)
        if result.state == 'SUCCESS':
            # Task succeeded, redirect
            return redirect(request.referrer)
        elif result.state == 'FAILURE':
            # Task failed, handle failure
            return jsonify({'error': 'Task failed'}), 500
        else:
            # Task is still pending or in progress, wait a bit and check again
            time.sleep(1)



@blueprint.route("/check", methods=["POST"])
@check_idproject
def check_remote(idproject):
    # Start the task
    task = checkRemote.delay(id_project=idproject,user_id=current_user.id)

    while True:
        result = AsyncResult(task.id, app=celery)
        if result.state == 'SUCCESS':
            flash('You were success checking commits!', 'success_check_commits')
            return redirect(request.referrer)
        elif result.state == 'FAILURE':
            # Task failed, handle failure
            return jsonify({'error': 'Task failed'}), 500
        else:
            # Task is still pending or in progress, wait a bit and check again
            time.sleep(1)
