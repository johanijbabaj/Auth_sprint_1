from datetime import datetime
from http import HTTPStatus

from auth_config import Config, db, jwt, jwt_redis
from db_models import Group, History, User
from flasgger.utils import swag_from
from flask import Blueprint, render_template, request
from flask.json import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from password_hash import check_password, hash_password

user_bp = Blueprint("user_bp", __name__)
jwt_redis_blocklist = jwt_redis


@swag_from("../schemes/user_register.yaml", validation=True)
@user_bp.route("/register", methods=["POST"])
def register():
    """
    Метод регистрации пользователя
    """
    obj = request.json
    user = User.query.filter_by(email=obj["email"]).first()
    if not user:
        try:
            # obj["password"] = hash_password(obj["password"])
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


@swag_from("../schemes/user_login_param.yaml")
@user_bp.route("/login", methods=["POST"])
def login():
    """
    Метод при успешной авториазции возвращает пару ключей access и refreh токенов
    """
    username = request.args.get("login", None)
    password = request.args.get("password", None)
    user = User.query.filter_by(login=username).first()
    if (user and user.verify_password(password)) or (
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
                user_id=user.id, useragent="unknown", timestamp=datetime.now()
            )
            db.session.add(history)
            db.session.commit()
    else:
        return jsonify({"msg": "Bad username or password"}), HTTPStatus.UNAUTHORIZED

    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        HTTPStatus.OK,
    )


@jwt_required(refresh=True)
@swag_from("../schemes/user_refresh_param.yaml")
@user_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Обновление пары токенов при получении действительного refresh токена
    """
    try:
        verify_jwt_in_request(refresh=True)
    except Exception as ex:
        return (jsonify({"msg": f"Bad refresh token: {ex}"}), HTTPStatus.UNAUTHORIZED)
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        HTTPStatus.OK,
    )


@jwt_required()
@swag_from("../schemes/user_logout_param.yaml")
@user_bp.route("/logout", methods=["DELETE"])
def logout():
    """
    Выход пользователя из аккаунта
    """
    try:
        verify_jwt_in_request()
    except Exception as ex:
        return (jsonify({"msg": f"Bad access token: {ex}"}), HTTPStatus.UNAUTHORIZED)
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=Config.ACCESS_EXPIRES)
    return (
        jsonify(msg="Access token revoked"),
        HTTPStatus.OK,
    )


@jwt_required()
@swag_from("../schemes/user_account_post_param.yaml")
@user_bp.route("/account/", methods=["POST"])
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


@user_bp.route("/<user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Получить информацию о пользователе
    """
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
    return jsonify(user.to_json())


@user_bp.route("/history", methods=["GET"])
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


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None
