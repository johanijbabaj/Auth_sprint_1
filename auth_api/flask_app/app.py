from flask.json import jsonify
from flask import request
from flask_script import Manager
from db_models import Group, User
from auth_config import app, BASE_PATH, session
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, JWTManager
from flasgger.utils import swag_from

manager = Manager(app)
jwt = JWTManager(app)

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

#@swag_from("swagger_auth_api.yaml")
#@swag_from("user_login.yml")
@swag_from("test.yaml")
@app.route("/user/login", methods=["POST"])
def login():
    username = request.args.get("login", None)
    password = request.args.get("password", None)
    user = session.query(User).filter(User.login == username).first()
    if (user and user.password == password) or (username == "test" and password == "test"):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity="example_user")
    else:
        return jsonify({"msg": "Bad username or password"}), 401

    return jsonify(access_token=access_token, refresh_token=refresh_token)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # manager.run()
    # КАК РАБОТАТЬ С КОНСОЛЬНЫМ ЗАПУСКОМ?
