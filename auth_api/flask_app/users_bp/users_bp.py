from http import HTTPStatus

from flasgger.utils import swag_from
from flask import Blueprint, render_template, request
from flask.json import jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)

from auth_api.flask_app.db_models import User

users_bp = Blueprint("users_bp", __name__)


@users_bp.route("/", methods=["GET"])
def list_users():
    """
    Список всех зарегистрированных пользователей
    """
    users = []
    for user in User.query.all():
        users.append(user.to_json())
    return jsonify(users)
