"""Запуск основного приложения сервиса аутентификации"""
# flask_app/app.py
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, JWTManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db_models import User


engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres_auth/auth")
session = Session(bind=engine)

app = Flask(__name__)
jwt = JWTManager(app)


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'



if __name__ == '__main__':
    app.run(host='0.0.0.0')

