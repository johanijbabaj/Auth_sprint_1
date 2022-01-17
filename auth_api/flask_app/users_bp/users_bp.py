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
    page_size = request.args.get("page_size", None)
    page_number = request.args.get("page_number", 1)
    if page_size is None:
        for user in User.query.order_by(User.login).all():
            users.append(user.to_json())
    else:
        for user in (
            User.query.order_by(User.login)
            .paginate(int(page_number), int(page_size), False)
            .items
        ):
            users.append(user.to_json())
    return jsonify(users), HTTPStatus.OK
