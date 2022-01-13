"""МОдуль основного приложения"""
import datetime
import os
import sys
from http import HTTPStatus

from auth_config import BASE_PATH, Config, app, db, jwt_redis
from db_models import Group, History, User, UserGroup
from flasgger.utils import swag_from
from flask import request
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
from flask_script import Manager
from password_hash import check_password, hash_password

manager = Manager(app)
jwt = JWTManager(app)
jwt_redis_blocklist = jwt_redis


@app.route("/test", methods=["GET"])
def test():
    """
    Тестовый роут
    :return: It works!
    """
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


@swag_from("user_register.yaml", validation=True)
@app.route(f"{BASE_PATH}/user/register", methods=["POST"])
def register():
    """
    Метод регистрации пользователя
    """
    obj = request.json
    user = User.query.filter_by(email=obj["email"]).first()
    if not user:
        try:
            #obj["password"] = hash_password(obj["password"])
            user = User(**obj)
            db.session.add(user)
            db.session.commit()
            return jsonify({"msg": "User was successfully registered"}), HTTPStatus.OK

        except Exception as err:
            return jsonify({"msg": f"Unexpected error: {err}"}), HTTPStatus.CONFLICT

    else:
        return (
            jsonify(
                {"msg": "User had already been registered. Check the email, id, login"}
            ),
            HTTPStatus.CONFLICT,
        )


@swag_from("user_login_param.yaml")
@app.route(f"{BASE_PATH}/user/login", methods=["POST"])
def login():
    """
    Метод при успешной авториазции возвращает пару ключей access и refreh токенов
    """
    username = request.args.get("login", None)
    password = request.args.get("password", None)
    user = User.query.filter_by(login=username).first()

    if (user and user.check_password(password)) or (
        username == "test" and password == "test"
    ):
        if username == "test":
            user_identity = username
        else:
            user_identity = str(user.id)
        access_token = create_access_token(identity=user_identity)
        refresh_token = create_refresh_token(identity=user_identity)
        if user:
            # Добавить информацию о входе в историю
            history = History(
                user_id=user.id, useragent="unknown", timestamp=datetime.datetime.now()
            )
            db.session.add(history)
            db.session.commit()
    else:
        return jsonify({"msg": "Bad username or password"}), HTTPStatus.UNAUTHORIZED

    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        HTTPStatus.OK,
    )


@jwt_required()
@swag_from("user_refresh_param.yaml")
@app.route(f"{BASE_PATH}/user/refresh", methods=["POST"])
def refresh():
    """
    Обновление пары токенов при получении действительного refresh токена
    """
    try:
        verify_jwt_in_request(refresh=True)
    except Exception as ex:
        return jsonify({"msg": f"Bad refresh token: {ex}"}), HTTPStatus.UNAUTHORIZED
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        HTTPStatus.OK,
    )


@jwt_required()
@swag_from("user_logout_param.yaml")
@app.route(f"{BASE_PATH}/user/logout", methods=["DELETE"])
def logout():
    """
    Выход пользователя из аккаунта
    """
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=Config.ACCESS_EXPIRES)
    return (
        jsonify(msg="Access token revoked"),
        HTTPStatus.OK,
    )


@jwt_required()
@swag_from("user_account_post_param.yaml")
@app.route(f"{BASE_PATH}/user/account/", methods=["POST"])
def update():
    """
    Обновление данных пользователя
    """
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    obj = request.json
    obj["password"] = hash_password(obj["password"])
    updated_user = user.from_json(obj)
    return (
        jsonify(msg=f"Update success: {updated_user}"),
        HTTPStatus.OK,
    )


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """
    Проверяем был ли отозван токен
    :param jwt_header: Заголовок JWT токена
    :param jwt_payload: Полезные данные токвна
    :return: TRUE/FALSE
    """
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@app.route(f"{BASE_PATH}/groups/", methods=["POST"])
@jwt_required()
def create_group():
    """
    Создать новую группу
    """
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.from_json(request.json)
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_json())


@app.route(f"{BASE_PATH}/group/<group_id>/", methods=["GET"])
def get_group(group_id):
    """
    Получить информацию о группе
    """
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    return jsonify(group.to_json())


@app.route(f"{BASE_PATH}/group/<group_id>/", methods=["DELETE"])
@jwt_required()
def del_group(group_id):
    """
    Удалить группу
    """
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"result": "Group did not exist"})
    db.session.delete(group)
    db.session.commit()
    return jsonify({"result": "Group deleted"})


@app.route(f"{BASE_PATH}/group/<group_id>/", methods=["PUT"])
@jwt_required()
def update_group(group_id):
    """
    Изменить группу
    """
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


@app.route(f"{BASE_PATH}/group/<group_id>/users/", methods=["POST"])
@jwt_required()
def add_group_user(group_id):
    """
    Добавить пользователя в группу
    """
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    group = Group.query.get(group_id)
    if group is None:
        return jsonify({"error": "group not found"}), HTTPStatus.NOT_FOUND
    user_id = request.json["user_id"]
    membership = UserGroup(user_id=user_id, group_id=group_id)
    db.session.add(membership)
    db.session.commit()
    return jsonify({"result": f"User {user_id} added to group {group_id}"})


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


@app.route(f"{BASE_PATH}/group/<group_id>/user/<user_id>", methods=["GET"])
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
    membership = (
        UserGroup.query.filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    )
    if membership is None:
        return jsonify({"error": "user is not in the group"}), HTTPStatus.NOT_FOUND
    return jsonify(membership.to_json())


@app.route(f"{BASE_PATH}/group/<group_id>/user/<user_id>", methods=["DELETE"])
@jwt_required()
def del_membership(group_id, user_id):
    """
    Удалить пользователя из группы
    """
    current_user = User.query.get(get_jwt_identity())
    if not current_user or not current_user.is_admin():
        return jsonify({"error": "Only administrators may do it"}), HTTPStatus.FORBIDDEN
    membership = (
        UserGroup.query.filter_by(group_id=group_id).filter_by(user_id=user_id).first()
    )
    if membership is None:
        return jsonify({"result": "user was not in the group"})
    db.session.delete(membership)
    db.session.commit()
    return jsonify({"result": "user removed from the group"})


@app.route(f"{BASE_PATH}/user/history", methods=["GET"])
@jwt_required()
def get_user_history():
    """
    Получить историю операций пользователя
    """
    current_user = User.query.get(get_jwt_identity())
    if not current_user:
        return jsonify({"error": "No such user"}), HTTPStatus.NOT_FOUND
    history = current_user.get_history()
    return jsonify([h.to_json() for h in history.all()])


def db_initialize():
    """
    Первоначальная инициализация приложения авторизации

        Инициализируем структуру таблиц, создаем группу
        администраторов и одного пользователя, входящего
        в нее, а также одного пользователя не входящего
        ни в какие группы. Пароли пользователей берутся
        из переменных окружения ADMIN_PASSWORD и
        NOBODY_PASSWORD.

        Эта функция предназначена для начальной инициализации
        базы и уничтожит все имеющиеся данные в ней
    """
    try:
        db.drop_all()
    except Exception:
        pass
    db.create_all()
    admin_group = Group(name="admin", description="Administrators")
    admin_user = User(
        login="admin",
        email="root@localhost",
        password="",
        full_name="Site administrator",
    )
    regular_user = User(
        login='nobody',
        email='nobody@localhost',
        password_hash='',
        full_name='Regular user'
    )
    # Берем пароли из переменных окружения
    admin_user.password = os.getenv('ADMIN_PASSWORD')
    regular_user.password = os.getenv('NOBODY_PASSWORD')
    db.session.add(admin_group)
    db.session.add(admin_user)
    db.session.add(regular_user)
    db.session.commit()
    # Только после первого коммита пользователь и группа получат
    # автосгенерированные UUID
    admin_membership = UserGroup(user_id=admin_user.id, group_id=admin_group.id)
    db.session.add(admin_membership)
    db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) == 1 and sys.argv[0] == "--initialize":
        db_initialize()
    app.run(host="0.0.0.0")
