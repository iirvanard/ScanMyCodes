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

from app.tasks.project_detail.delete_project import delete_project_task
from app.tasks.project_detail.update_project import updateProject
from app.tasks.project_detail.check_remote import checkRemote
from psycopg2.errors import UniqueViolation
import traceback