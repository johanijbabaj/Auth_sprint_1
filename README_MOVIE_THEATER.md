# Ссылка на репозиторий
https://github.com/johanijbabaj/Async_API_sprint_2/

# Настройка

## Настройка Postgres
- Настройка переменных окружения. Создайте файл db.env, и укажите в неё значения: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD (в качестве примера можно взять файл db.env.example)
- Добавление файлов БД. Создайте в корне проекта папку pgdata, и поместите туда файлы БД (можно использовать вот эти https://drive.google.com/file/d/1INh4uMXfcJfNXhisvVBWrJ_kDNxFoziT/view?usp=sharing)
- 
## Настройка Django
- Настройка переменных окружения. Создайте файл movies_admin/.env, и укажите в неё значения: SECRET_KEY, ALLOWED_HOSTS, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT (в качестве примера можно взять файл movies_admin/.env.example)

## Настройка ETL
- Создание конфигурации. В конфигурационном файле postgres_to_es/settings/settings.json (файл нужно создать, в качестве примера можно взять файл postgres_to_es/settings/settings.json.example) необходимо указать параметры подключения к Postgres и Elasticsearch.

## Настройка FastAPI
- Настройка переменных окружения. Создайте файл fa.env, и укажите в нем значения: PROJECT_NAME, REDIS_HOST, REDIS_PORT, REDIS_AUTH, ELASTIC_HOST, ELASTIC_PORT (в качестве примера можно взять файл fa.env.example)

# Взаимодействие
- Доступ к документации FastAPI осуществляется через http://localhost:8000/api/openapi
- Доступ к админке Django осуществляется через http://localhost/admin/ (user admin, password 123456)
