"""Запуск основного приложения сервиса аутентификации"""
# flask_app/app.py
from flask import Flask


app = Flask(__name__)


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
