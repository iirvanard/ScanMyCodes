from flask import Blueprint, render_template

blueprint = Blueprint('index', __name__, url_prefix='/')

from app.models.users import User


@blueprint.route("/", methods=["GET"])
def index():
    users = User.query.all()
    serialized_users = []

    for user in users:
        serialized_user = {
            'id': user.id,
            'username': user.username,
        }
        serialized_users.append(serialized_user)

    return render_template("index.html", title="index")
