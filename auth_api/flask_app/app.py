from flask.json import jsonify
from flask_script import Manager

from db_models import Group

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
        return jsonify({'error': 'group not found'})
    return jsonify(group.to_json())


@app.route(f"{BASE_PATH}/group/<group_id>/users/", methods=['GET'])
def list_group_users(group_id):
    """
        Список пользователей, входящих в определенную группу.
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({'error': 'group not found'})
    users = group.get_all_users()
    answer = []
    for user in users.all():
        answer.append(user.to_json())
    return jsonify(answer)


if __name__ == '__main__':
    manager.run()
