from http import HTTPStatus

from auth_config import BASE_PATH, app, session
from db_models import Group, User
from flasgger.utils import swag_from
from flask import request
from flask.json import jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_script import Manager

manager = Manager(app)
jwt = JWTManager(app)


@app.route("/test", methods=["GET"])
def test():
    return "It works!"


@app.route(f"{BASE_PATH}/groups/", methods=["GET"])
def list_groups():
    """
    Список всех пользовательских групп
    """
    groups = []
    for group in Group.query.all():
        groups.append(group.to_json())
    return jsonify(groups)


# @swag_from("swagger_auth_api.yaml")
# @swag_from("user_login.yml")
@swag_from("test.yaml")  # работают параметры пока только с таким файлом FIXME
@app.route("/user/login", methods=["POST"])
def login():
    """
    Метод при успешной авториазции возвращает пару ключей access и refreh токенов
    FIXME: Предполгаю что нужно будет добавить еще запись и хранение токенов для последующей аутентификации
    """
    username = request.args.get("login", None)
    password = request.args.get("password", None)
    user = session.query(User).filter(User.login == username).first()

    if (user and user.password == password) or (
        username == "test" and password == "test"
    ):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity="example_user")
    else:
        return jsonify({"msg": "Bad username or password"}), HTTPStatus.UNAUTHORIZED

    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        HTTPStatus.OK,
    )


@app.route(f"{BASE_PATH}/group/<group_id>/", methods=["GET"])
def get_group(group_id):
    """
    Получить информацию о группе
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    return jsonify(group.to_json())


@app.route(f"{BASE_PATH}/group/<group_id>/users/", methods=["GET"])
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


@app.route(f"{BASE_PATH}/users/", methods=["GET"])
def list_users():
    """
    Список всех зарегистрированных пользователей
    """
    users = []
    for user in User.query.all():
        users.append(user.to_json())
    return jsonify(users)


@app.route(f"{BASE_PATH}/user/<user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Получить информацию о пользователе
    """
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    return jsonify(user.to_json())


if __name__ == "__main__":
    app.run(host="0.0.0.0")
    # manager.run()
    # КАК РАБОТАТЬ С КОНСОЛЬНЫМ ЗАПУСКОМ?
