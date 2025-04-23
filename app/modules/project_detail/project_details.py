from . import *
from .utils import *


blueprint = Blueprint('project', __name__, url_prefix='/project/<string:idproject>')

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
        flash("Missing collaborator_user", "error")
        return redirect(request.referrer)  # Redirect back to the previous page

    # Query the database for the user
    user = User.query.filter(
        (User.username == collaborator_user) | 
        (User.email == collaborator_user)
    ).first()
    
    if not user:
        flash("User not found", "error")
        return redirect(request.referrer)  # Redirect back to the previous page

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
        flash("Collaborator added successfully", "success")
        return redirect(request.referrer)  # Redirect back to the previous page
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")
        return redirect(request.referrer) 


@blueprint.route("/add_branch", methods=["POST"])
@check_idproject
def add_branch_collaborator(idproject):
    try:
        collaborator_id = request.form.get('collaborator_id')
        branch_id = request.form.get('branch')

        if not collaborator_id or not branch_id:
            raise ValueError("Collaborator ID and Branch ID are required.")

        new_access = CollaboratorAccess(
            collaborator_id=collaborator_id,
            branch_id=branch_id
        )
        
        db.session.add(new_access)
        db.session.commit()

        flash(f"Collaborator ID: {collaborator_id} has been added to branch {branch_id}.", "success")
        return redirect(request.referrer)  # Redirect to the previous page

    except UniqueViolation as e:
        db.session.rollback()
        # Extract only the relevant error message
        error_message = str(e).split("DETAIL:")[-1].strip()
        flash(f"Error: {error_message}", "error")
        return redirect(request.referrer)  # Redirect to the previous page

    except ValueError as ve:
        db.session.rollback()
        flash(f"Error: {ve}", "error")
        return redirect(request.referrer)  # Redirect to the previous page

    except Exception as e:
        db.session.rollback()
        # For general exceptions, just take the message
        error_message = str(e)
        flash(f"An error occurred: {error_message}", "error")
        return redirect(request.referrer)  # Redirect to the previous page


    



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
                flash('Invitation rejected successfully', 'success')
            
            return redirect(url_for('project.manage_invitation', idproject=idproject))

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

    collaborators = ProjectCollaborator.query.filter_by(project_id=str(UUID(idproject))).all()

    branches = get_branches(idproject)

    return render_template(
        '/project_detail/settings/index.html',
        project=project,
        repository=repo,
        openai=openai_data,
        collaborator=collaborators,
        branch=branches
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