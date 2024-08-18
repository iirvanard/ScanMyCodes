import os
import json
import time
from uuid import UUID
from functools import wraps

from flask import Blueprint, flash, abort, g, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc
from celery.result import AsyncResult

from app import celery, app
from app.extensions import db
from app.models import Project, GitBranch, GitRepository, OpenaiProject, AnalyzeIssue, ProjectLog, User,CollaboratorAccess
from app.models.project_collaborator import ProjectCollaborator
from app.tasks.project_detail import updateProject, delete_project_task, checkRemote

blueprint = Blueprint('project', __name__, url_prefix='/project/<string:idproject>')


# Utility Functions
def get_project_from_id(idproject):
    return Project.query.filter_by(project_id=idproject).first()


def get_branches(idproject):
    try:
        # Ambil proyek berdasarkan idproject
        project = get_project_from_id(idproject)
        
        # Periksa apakah proyek dimiliki oleh pengguna saat ini
        if project.user_id == current_user.id:
            # Ambil semua branch yang terkait dengan proyek
            branches = GitBranch.query.filter_by(project_id=idproject).all()
            return branches
        
        # Jika bukan pemilik, periksa kolaborator proyek
        project_collaborator = ProjectCollaborator.query.filter_by(
            project_id=idproject, collaborator_id=current_user.id
        ).first()

        # Jika kolaborator ditemukan dan memiliki akses
        if project_collaborator and project_collaborator.accesses:
            # Ambil daftar branch yang dapat diakses oleh kolaborator
            branches = [access.branch for access in project_collaborator.accesses]
            return branches
        
        # Jika tidak ada akses, kembalikan list kosong
        return []

    except Exception as e:
        # Log kesalahan yang terjadi dan kembalikan None
        return None



def marksdown(idproject, branch):
    try:
        branchx = GitBranch.query.filter_by(project_id=idproject, remote=branch).first()
        filename = AnalyzeIssue.query.filter_by(project_id=idproject, branch=branchx.id).first()
        dir_destination = os.path.join(app.config['STATIC_FOLDER_1'], "scan", filename.path_)

        if not os.path.exists(dir_destination) or os.path.getsize(dir_destination) == 0:
            raise FileNotFoundError(f"The file at {dir_destination} is empty or does not exist.")
        
        with open(dir_destination, encoding='utf-8') as user_file:
            filejson = user_file.read()
            if not filejson.strip():
                raise ValueError("The file is empty.")
            data = json.loads(filejson)
        
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
                return func(*args, **kwargs)

            g.collaborator = ProjectCollaborator.query.filter_by(
                project_id=idproject, collaborator_id=current_user.id).first()

            if g.collaborator:
                if g.collaborator.status == 'confirmed':
                    return func(*args, **kwargs)
                elif g.collaborator.status == 'pending':
                    return redirect(url_for('project.manage_invitation', idproject=g.project.project_id))
            
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



@blueprint.route("/invitations", methods=["POST", "GET"])
@login_required
def manage_invitation(idproject):
    g.project = get_project_from_id(idproject)
    g.collaborator = ProjectCollaborator.query.filter_by(project_id=idproject, collaborator_id=current_user.id).first()

    if g.collaborator and (g.collaborator.status == "confirmed" or g.project.user_id == current_user.id):
        return redirect(url_for('project.analysis', idproject=idproject))
    elif g.collaborator and g.collaborator.status == "rejected":
        abort(404)

    if request.method == "POST":
        try:
            invitation = ProjectCollaborator.query.filter_by(
                collaborator_id=current_user.id, project_id=idproject
            ).first()

            if not invitation:
                return jsonify({"error": "Invitation not found"}), 404

            if 'confirmed' in request.form:
                invitation.confirm()
                flash('Invitation confirmed successfully', 'success')
            elif 'rejected' in request.form:
                invitation.rejected()
                flash('Invitation confirmed successfully', 'success')
            
            return redirect(url_for('manage_invitation', idproject=idproject))

         
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    return render_template('/project_detail/invitations/invitation_page.html', idproject=idproject, project=g.project)
@blueprint.route("/analysis", methods=["GET"])
@blueprint.route("/analysis/<string:branchid>", methods=["GET"])
@check_idproject
def analysis(idproject, branchid=None):
    # Fetch project and branch details
    project = get_project_from_id(idproject)
    branch_names = [branch.remote for branch in get_branches(idproject)]
    gitrepo = GitRepository.query.filter_by(project_id=str(UUID(idproject))).first()
        
    # Memeriksa apakah status analisis proyek berhasil, branchid adalah None, dan default_branch tersedia di gitrepo
    if (project.analyze_status == "success" 
            and branchid is None 
            and gitrepo.default_branch 
            and branch_names):
        
        # Mengarahkan ke URL analisis proyek dengan idproject dan default_branch
        return redirect(url_for('project.analysis', idproject=project.project_id, branchid=gitrepo.default_branch))
    
    # Get analysis statistics and markdown content
    stats, markdown_content = marksdown(idproject, branchid)
    
    
    # Determine analysis content and page title
    analysis_content = render_analysis_content(markdown_content) if branchid else None
    title = f"Branch Dev - {project.project_name}" if branchid else f"Analysis - {project.project_name}"
    
    # Render the template with the appropriate context
    return render_template(
        '/project_detail/analysis/index.html',
        analysis_content=analysis_content if branch_names else [], 
        BranchName=branchid,
        stats=stats,
        branches=branch_names,
        title=title,
        project=project
    )




def render_analysis_content( markdown_content):
    """Render analysis content based on branchid."""
    filter_content = {
        'Severity': {"high", "medium", "critical", "low", "weak"},
        'Language': {"python", "php", "javascript"}
    }
    return render_template(
        '/project_detail/analysis/branch.html',
        filterContent=filter_content,
        content=markdown_content
    )


@blueprint.route('/log', methods=["GET"])
@check_idproject
def log(idproject):
    project = get_project_from_id(idproject)
    # Ambil log sesuai dengan hak akses pengguna
    filters = {'project_id': idproject}
    if project.user_id != current_user.id:
        filters['user_id'] = current_user.id

    logs = ProjectLog.query.filter_by(**filters).order_by(desc(ProjectLog.created_at)).all()

    return render_template(
        '/project_detail/log/log.html',
        title=f"Log - {project.project_name}",
        content=logs,
        project=project
    )



@blueprint.route('/log/<string:logid>')
@check_idproject
def log_by_id(idproject, logid):
    project = get_project_from_id(idproject)
    log = ProjectLog.query.filter_by(id=logid).first()
    dir_path = os.path.join(app.config['STATIC_FOLDER_1'], "log")
    log_file_path = os.path.join(dir_path, log.path_)

    try:
        with open(log_file_path, 'r') as file:
            content = [line.rstrip('\n') for line in file]
    except FileNotFoundError:
        content = ""

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
    task = delete_project_task.delay(idproject)
    while True:
        result = AsyncResult(task.id, app=celery)
        if result.state == 'SUCCESS':
            return redirect(url_for('projects.index'))
        elif result.state == 'FAILURE':
            return jsonify({'error': 'Task failed'}), 500
        time.sleep(1)


@blueprint.route("/update", methods=["POST"])
@check_idproject
@is_project_manager
def update_project(idproject):
    task = updateProject.delay(project_id=idproject, requests=request.form)
    while True:
        result = AsyncResult(task.id, app=celery)
        if result.state == 'SUCCESS':
            return redirect(request.referrer)
        elif result.state == 'FAILURE':
            return jsonify({'error': 'Task failed'}), 500
        time.sleep(1)


@blueprint.route("/check", methods=["POST"])
@check_idproject
def check_remote(idproject):
    task = checkRemote.delay(id_project=idproject, user_id=current_user.id)
    while True:
        result = AsyncResult(task.id, app=celery)
        if result.state == 'SUCCESS':
            flash('You successfully checked commits!', 'success_check_commits')
            return redirect(request.referrer)
        elif result.state == 'FAILURE':
            return jsonify({'error': 'Task failed'}), 500
        time.sleep(1)
