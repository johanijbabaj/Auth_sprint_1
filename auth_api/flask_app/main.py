# """Запуск основного приложения сервиса аутентификации"""
# # flask_app/app.py
# from datetime import timedelta
# from flask import Flask, jsonify, request
# from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, JWTManager
# <<<<<<< HEAD
# =======
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# from db_models import User
# >>>>>>> authissue13-login
#
#
# engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres_auth/auth")
# session = Session(bind=engine)
#
# app = Flask(__name__)
# <<<<<<< HEAD
# app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
# =======
# >>>>>>> authissue13-login
# jwt = JWTManager(app)
#
#
# @app.route('/hello-world')
# def hello_world():
#     return 'Hello, World!'
#
# @app.route("/login", methods=["POST"])
# def login():
#     username = request.json.get("username", None)
#     password = request.json.get("password", None)
#     if username != "test" or password != "test":
#         return jsonify({"msg": "Bad username or password"}), 401
#
#     access_token = create_access_token(identity=username)
#     refresh_token = create_refresh_token(identity="example_user")
#
#     return jsonify(access_token=access_token, refresh_token=refresh_token)
#
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
#
