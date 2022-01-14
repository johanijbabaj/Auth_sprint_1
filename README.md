# Информация для Наставника.

- Описание используемых технологий находится тут:
[here](docs/description.md)
- Описание API:
/docs/swagger_auth_api.yaml
- Схема базы данных:
/schema/db_schema.sql
- ORM модели:
/flask_app/db_models.py

# Информация для ревьювера

## Запуск основного docker-compose с сервисами авториазции:

[here](docker-compose.yml)
Предварительно:
* убрать у файла [here](auth.env.example) расщирение example
* убрать у файла [here](db_auth.env.example) расширение example

После запуска по адресу [url](http://flask_auth_api:5000/apidocs/) swagger схема с описанием для проверки работы сервисов

## Запуск docker-compose c тестами:

[here](tests/auth_api/docker-compose.yml)
Предварительно:
* убрать у файла [here](tests/auth_api/auth.env.example) расширение example
* убрать у файла [here](tests/auth_api/db_auth.env.example) расширение example
