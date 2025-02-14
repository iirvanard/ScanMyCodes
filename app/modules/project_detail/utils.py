from . import *
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