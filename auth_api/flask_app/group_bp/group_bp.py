from http import HTTPStatus

from auth_config import db
from db_models import Group, User
from flasgger.utils import swag_from
from flask import Blueprint, render_template, request
from flask.json import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

group_bp = Blueprint("group_bp", __name__)


@jwt_required()
@swag_from("../schemes/group_post.yaml")
@group_bp.route("/", methods=["POST"])
def create_group():
    """
    Создать новую группу
    """
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.from_json(request.json)
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_json())


@swag_from("../schemes/group_get.yaml")
@group_bp.route("/<group_id>/", methods=["GET"])
def get_group(group_id):
    """
    Получить информацию о группе
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    return jsonify(group.to_json())


@jwt_required()
@swag_from("../schemes/group_del.yaml")
@group_bp.route("/<group_id>/", methods=["DELETE"])
def del_group(group_id):
    """
    Удалить группу
    """
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"result": "Group did not exist"})
    db.session.delete(group)
    db.session.commit()
    return jsonify({"result": "Group deleted"})


@jwt_required()
@swag_from("../schemes/group_put.yaml")
@group_bp.route("/<group_id>/", methods=["PUT"])
def update_group(group_id):
    """
    Изменить группу
    """
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    if "name" in request.json:
        group.name = request.json["name"]
    if "description" in request.json:
        group.name = request.json["description"]
    db.session.add(group)
    db.session.commit()
    return jsonify({})


@swag_from("../schemes/group_users_get.yaml", methods=["GET"])
@group_bp.route("/<group_id>/users/", methods=["GET"])
def list_group_users(group_id):
    """
    Список пользователей, входящих в определенную группу.
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    users = group.get_all_users()
    answer = []
    for user in users.all():
        answer.append(user.to_json())
    return jsonify(answer)


@jwt_required()
@swag_from("../schemes/group_user_post.yaml", methods=["POST"])
@group_bp.route("/<group_id>/users/", methods=["POST"])
def add_group_user(group_id):
    """
    Добавить пользователя в группу
    """
    # FIXME: удалить после слияния
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    # FIXME: Через Swagger работает вот так проверить тесты
    user_id = request.args["user_id"]
    # user_id = request.json["user_id"]
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    group.users.append(user)
    db.session.add(group)
    db.session.commit()
    return jsonify({"result": f"User {user_id} added to group {group_id}"})


@swag_from("../schemes/group_user_check_get.yaml", methods=["GET"])
@group_bp.route("/<group_id>/user/<user_id>", methods=["GET"])
def get_membership(group_id, user_id):
    """
    Получить информацию о членстве пользователя user_id в группе
    group_id. Если пользователь в группу не входит, вернуть ответ
    404. Иначе возвращается ответ следующего вида с кодом 200
    {
        'user_id': <user_id>,
        'group_id': <group_id>
    }
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    if user not in group.users:
        return jsonify({"error": "user is not in the group"}), HTTPStatus.NOT_FOUND
    return jsonify({"user_id": user_id, "group_id": group_id})


@jwt_required()
@swag_from("../schemes/group_user_del.yaml", methods=["DELETE"])
@group_bp.route("/<group_id>/user/<user_id>", methods=["DELETE"])
def del_membership(group_id, user_id):
    """
    Удалить пользователя из группы
    """
    # FIXME: удалить после слияния
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    if user in group.users:
        group.users.remove(user)
        db.session.add(group)
        db.session.commit()
        return jsonify({"result": "user removed from the group"}), HTTPStatus.OK
    else:
        return jsonify({"result": "user was not in the group"}), HTTPStatus.NOT_FOUND
