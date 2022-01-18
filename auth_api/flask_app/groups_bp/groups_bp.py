from http import HTTPStatus

from auth_config import db
from db_models import Group, User
from decorators import admin_required
from flasgger.utils import swag_from
from flask import Blueprint, render_template, request
from flask.json import jsonify

groups_bp = Blueprint("groups_bp", __name__)


@swag_from("../schemes/groups_get.yaml")
@groups_bp.route("/", methods=["GET"])
def list_groups():
    """
    Список всех пользовательских групп
    """
    groups = []
    for group in Group.query.all():
        groups.append(group.to_json())
    return jsonify(groups)


@groups_bp.route("/", methods=["POST"])
@admin_required()
@swag_from("../schemes/group_post.yaml")
def create_group():
    """
    Создать новую группу
    """
    group = Group.query.get(request.json["id"])
    if group is not None:
        return jsonify("Group already exist")
    group = Group.from_json(request.json)
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_json())


@swag_from("../schemes/group_get.yaml")
@groups_bp.route("/<group_id>/", methods=["GET"])
def get_group(group_id):
    """
    Получить информацию о группе
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    return jsonify(group.to_json())


@groups_bp.route("/<group_id>/", methods=["DELETE"])
@admin_required()
@swag_from("../schemes/group_del.yaml")
def del_group(group_id):
    """
    Удалить группу
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"result": "Group did not exist"})
    db.session.delete(group)
    db.session.commit()
    return jsonify({"result": "Group deleted"})


@swag_from("../schemes/group_put.yaml")
@admin_required()
@groups_bp.route("/<group_id>/", methods=["PUT"])
def update_group(group_id):
    """
    Изменить группу
    """
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
@groups_bp.route("/<group_id>/users/", methods=["GET"])
def list_group_users(group_id):
    """
    Список пользователей, входящих в определенную группу.
    """
    page_size = request.args.get("page_size", 1)
    page_number = request.args.get("page_number", 1)
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    users = group.get_all_users()
    answer = []
    if page_size is None:
        for user in users:
            answer.append(user.to_json())
    else:
        for user in users.paginate(int(page_number), int(page_size), False).items:
            answer.append(user.to_json())
    return jsonify(answer)


@groups_bp.route("/<group_id>/users/", methods=["POST"])
@admin_required()
@swag_from("../schemes/group_user_post.yaml", methods=["POST"])
def add_group_user(group_id):
    """
    Добавить пользователя в группу
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    # FIXME: Через Swagger не работает
    # user_id = request.args["user_id"]
    user_id = request.json["user_id"]
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    group.users.append(user)
    db.session.add(group)
    db.session.commit()
    return jsonify({"result": f"User {user_id} added to group {group_id}"})


@swag_from("../schemes/group_user_check_get.yaml", methods=["GET"])
@groups_bp.route("/<group_id>/user/<user_id>", methods=["GET"])
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


@admin_required()
@swag_from("../schemes/group_user_del.yaml", methods=["DELETE"])
@groups_bp.route("/<group_id>/user/<user_id>", methods=["DELETE"])
def del_membership(group_id, user_id):
    """
    Удалить пользователя из группы
    """
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
