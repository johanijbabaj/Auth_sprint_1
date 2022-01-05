from flask.json import jsonify
from flask_script import Manager

from http import HTTPStatus

from db_models import Group, User

from auth_config import app, BASE_PATH

manager = Manager(app)


@app.route(f"{BASE_PATH}/groups/", methods=['GET'])
def list_groups():
    """
        Список всех пользовательских групп
    """
    groups = []
    for group in Group.query.all():
        groups.append(group.to_json())
    return jsonify(groups)


@app.route(f"{BASE_PATH}/group/<group_id>/", methods=['GET'])
def get_group(group_id):
    """
        Получить информацию о группе
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({'error': 'group not found'}), HTTPStatus.NOT_FOUND
    return jsonify(group.to_json())


@app.route(f"{BASE_PATH}/group/<group_id>/users/", methods=['GET'])
def list_group_users(group_id):
    """
        Список пользователей, входящих в определенную группу.
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({'error': 'group not found'}), HTTPStatus.NOT_FOUND
    users = group.get_all_users()
    answer = []
    for user in users.all():
        answer.append(user.to_json())
    return jsonify(answer)


@app.route(f"{BASE_PATH}/users/", methods=['GET'])
def list_users():
    """
        Список всех зарегистрированных пользователей
    """
    users = []
    for user in User.query.all():
        users.append(user.to_json())
    return jsonify(users)


@app.route(f"{BASE_PATH}/user/<user_id>/", methods=['GET'])
def get_user(user_id):
    """
        Получить информацию о пользователе
    """
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'user not found'}), HTTPStatus.NOT_FOUND
    return jsonify(user.to_json())


if __name__ == '__main__':
    manager.run()
