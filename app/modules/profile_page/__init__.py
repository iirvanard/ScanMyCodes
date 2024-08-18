from flask import Blueprint, render_template
from flask_login import current_user, login_required


blueprint = Blueprint('/settings', __name__, url_prefix='/settings')

from app.models import User


@blueprint.route("/", methods=["GET"])
@login_required
def profile():
    users = User.query.all()
    serialized_users = []

    for user in users:
        serialized_user = {
            'id': user.id,
            'username': user.username,
        }
        serialized_users.append(serialized_user)

    return render_template("profile_page/index.html", title="dashboard")
