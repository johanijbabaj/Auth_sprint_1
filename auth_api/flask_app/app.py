from flask.json import jsonify
from flask_script import Manager

from db_models import Group

from auth_config import app, BASE_PATH

manager = Manager(app)


# метод для проверки работы, пожалуйста не удаляйте
@app.route("/test", methods=['GET'])
def test():
    return 'It works!'


@app.route(f"{BASE_PATH}/group/update", methods=['PUT', 'POST'])
def create_update_group():
    """
        Создать новую либо обновить существующую группу пользователей
    """
    return jsonify({})


@app.route(f"{BASE_PATH}/group/all", methods=['GET'])
def list_groups():
    """
        Список всех пользовательских групп
    """
    groups = []
    for group in Group.query.all():
        groups.append(
            {
                'id': group.id,
                'name': group.name,
                'description': group.description
            }
        )
    return jsonify(groups)


if __name__ == '__main__':
    manager.run()
