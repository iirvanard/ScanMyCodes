from flask import Blueprint, jsonify

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
            'created_at':
            user.created_at.strftime('%Y-%m-%d'),  # Convert datetime to string
            'role': user.role
        }
        serialized_users.append(serialized_user)

    return jsonify(serialized_users)
