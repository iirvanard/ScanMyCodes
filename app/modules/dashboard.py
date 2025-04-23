from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask import redirect,url_for

blueprint = Blueprint('index', __name__, url_prefix='/')

from app.models import User


@blueprint.route("/", methods=["GET"])
@login_required
def index():
    
    return redirect(url_for('projects.index'))
    # users = User.query.all()
    # serialized_users = []

    # for user in users:
    #     serialized_user = {
    #         'id': user.id,
    #         'username': user.username,
    #     }
    #     serialized_users.append(serialized_user)

    # return render_template("index.html", title="dashboard")
