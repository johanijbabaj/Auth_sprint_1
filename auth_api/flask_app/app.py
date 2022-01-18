"""
Основной модуль
"""

import logging
import os
import sys

from auth_config import Config, db, jwt, jwt_redis
from db_models import Group, User
from flasgger import Swagger
from flask import Flask
from groups_bp.groups_bp import groups_bp
from password_hash import check_password, hash_password
from test_bp.test_bp import test_bp
from users_bp.users_bp import users_bp

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
            admin_group.users.append(admin_user)
            db.session.add(admin_group)
            db.session.commit()
        except Exception as ex:
            logging.error(f"we have a problem: {ex}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    app.register_blueprint(groups_bp, url_prefix=f"{BASE_PATH}/groups")
    app.register_blueprint(users_bp, url_prefix=f"{BASE_PATH}/users")
    app.register_blueprint(test_bp, url_prefix="/test")

    swagger = Swagger(app, template=Config.SWAGGER_TEMPLATE)
    db.init_app(app)
    engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
    engine.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    jwt.init_app(app)
    # manager = Manager.init(app)
    return app


if __name__ == "__main__":
    app = create_app()
    # При прогоне тестов удаляем прошлые данные из базы и создаем заново
    with app.app_context():
        if len(sys.argv) == 2 and sys.argv[1] == "--reinitialize":
            db.drop_all()
        # Инициалиазции базы
        try:
            user = User.query.filter_by(login="admin").first()
        except BaseException as ex:
            # Проверяем  по содержимому ошибки созданы ли таблицы
            # if "(psycopg2.errors.UndefinedTable)" in ex.args[0]:
            logging.info(f"initializing : {ex}")
            db_initialize(app)
            # logging.error(f"Unknown error: {ex}")
        app.run(host="0.0.0.0")
