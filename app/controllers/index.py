# encoding: utf-8

from flask import Blueprint, render_template

blueprint = Blueprint('index', __name__, url_prefix='/')


@blueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html")
