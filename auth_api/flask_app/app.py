"""
Основной модуль
"""

import datetime
import logging
import os
import sys
from http import HTTPStatus

from auth_config import Config, db, jwt, jwt_redis
from db_models import Group, User
from flasgger import Swagger
from flasgger.utils import swag_from
from flask import Flask, request
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
from group_bp.group_bp import group_bp
from groups_bp.groups_bp import groups_bp
from password_hash import check_password, hash_password
from user_bp.user_bp import user_bp
from users_bp.users_bp import users_bp

# , UserGroup

BASE_PATH = "/v1"


def db_initialize(app):
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
    with app.app_context():
        try:
            db.close_all_sessions()
            db.drop_all()
        except Exception as ex:
            logging.error(f"we have a problem: {ex}")
        db.create_all()
    admin_group = Group(name="admin", description="Administrators")
    admin_user = User(
        login="admin",
        email="root@localhost",
        password_hash="",
        full_name="Site administrator",
    )
    regular_user = User(
        login="nobody",
        email="nobody@localhost",
        password_hash="",
        full_name="Regular user",
    )
    # Берем пароли из переменных окружения
    admin_user.password = os.getenv("ADMIN_PASSWORD")
    regular_user.password = os.getenv("NOBODY_PASSWORD")
    db.session.add(admin_group)
    db.session.add(admin_user)
    db.session.add(regular_user)
    db.session.commit()
    # Только после первого коммита пользователь и группа получат
    # автосгенерированные UUID
    admin_membership = ""
    # UserGroup(user_id=admin_user.id, group_id=admin_group.id)
    db.session.add(admin_membership)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    app.register_blueprint(groups_bp, url_prefix="/groups")
    app.register_blueprint(group_bp, url_prefix="/group")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(user_bp, url_prefix="/user")

    swagger = Swagger(app, template=Config.SWAGGER_TEMPLATE)
    db.init_app(app)
    # engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
    # engine.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    jwt.init_app(app)
    # manager = Manager(app)

    return app


if __name__ == "__main__":
    app = create_app()
    # Инициалиазции базы
    # try:
    # user = User.query.filter_by(login="admin").first()
    #    except BaseException as ex:
    # Проверяем  по содержимому ошибки созданы ли таблицы
    # if "(psycopg2.errors.UndefinedTable)" in ex.args[0]:
    # logging.info(f"initializing : {ex}")
    db_initialize(app)
    # logging.error(f"Unknown error: {ex}")
    app.run(host="0.0.0.0")


@app.route("/test", methods=["GET"])
def test():
    return "It works!"
