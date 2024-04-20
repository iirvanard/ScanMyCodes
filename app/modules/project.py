from functools import wraps
from flask import Blueprint, abort, jsonify, flash, redirect, render_template, url_for
from app.models.project import Project
from flask_login import current_user


blueprint = Blueprint('project',
                      __name__,
                      url_prefix='/project/<string:idproject>')


def check_idproject(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            idproject = kwargs.get('idproject')
            project = Project.query.filter_by(project_id=idproject).first()
            if not project or project.username != current_user.username:
                raise None
        
        except Exception:
            abort(404)
        return func(*args, **kwargs)

    return decorated_function


@blueprint.route("/", methods=["GET"])
@check_idproject
def index(idproject):
    return redirect(url_for('project.analysis', idproject=idproject))


@blueprint.route("/analysis", methods=["GET"])
@check_idproject
def analysis(idproject):
    return render_template("/project/analysis/index.html",
                           title="project title",
                           idproject=idproject)


@blueprint.route("/analysis/<string:branchid>", methods=["GET"])
@check_idproject
def analysisByBranch(idproject, branchid):
    analysis_content = render_template("/project/analysis/branch.html")
    return render_template('/project/analysis/index.html',
                           analysis_content=analysis_content,
                           BranchName=branchid,
                           title="branch dev",
                           idproject=idproject)


@blueprint.route('/log', methods=["GET"])
@check_idproject
def log(idproject):
    return render_template('/project/log/log.html',
                           logid="asdasd",
                           title="log - 12313123",
                           idproject=idproject)


@blueprint.route('/log/<string:logid>')
@check_idproject
def log_by_id(logid, idproject):
    return render_template('/project/log/log_item.html',
                           title="Log details - 123123",
                           idproject=idproject,
                           logid=logid)


@blueprint.route('/settings')
@check_idproject
def settings(idproject):
    return render_template('/project/settings/index.html', idproject=idproject)
