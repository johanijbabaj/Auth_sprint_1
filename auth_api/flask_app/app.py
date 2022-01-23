"""
Основной модуль
"""

import logging
import os
import shutil
import sys
import time

from auth_config import Config, db, engine, insp, jwt, jwt_redis, migrate_obj
from db_models import Group, User
from flasgger import Swagger
from flask import Flask
from flask_migrate import init, migrate, upgrade

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
        # FIXME: удалить после добавления WSGI сервера
        time.sleep(5)
        try:
            db.close_all_sessions()
            db.drop_all()
            if os.path.isdir(Config.MIGRATIONS_PATH):
                shutil.rmtree(Config.MIGRATIONS_PATH)
                engine.execute("DELETE FROM alembic_version")
            init(Config.MIGRATIONS_PATH)
            migrate(Config.MIGRATIONS_PATH)
            upgrade(Config.MIGRATIONS_PATH)
            # db.create_all()
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
    # engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
    engine.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    jwt.init_app(app)
    migrate_obj.init_app(app, db)

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # При прогоне тестов удаляем прошлые данные из базы и создаем заново
        if len(sys.argv) == 2 and sys.argv[1] == "--reinitialize":
            db.drop_all()
        # Инициалиазции базы. Проверяем наличие таблицы пользователей
        if not insp.has_table("user", schema="auth"):
            logging.info(f"initializing...")
            db_initialize(app)
        app.run(host="0.0.0.0")
