from http import HTTPStatus

from db_models import User
from flasgger.utils import swag_from
from flask import Blueprint, render_template, request
from flask.json import jsonify

users_bp = Blueprint("users_bp", __name__)


@swag_from("../schemes/users_get.yaml", methods=["GET"])
@users_bp.route("/", methods=["GET"])
def list_users():
    """
    Список всех зарегистрированных пользователей
    """
    users = []
    for user in User.query.all():
        users.append(user.to_json())
    return jsonify(users), HTTPStatus.OK
