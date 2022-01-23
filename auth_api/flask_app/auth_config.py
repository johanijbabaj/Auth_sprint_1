import os
from datetime import timedelta

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, inspect

import redis


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    ACCESS_EXPIRES = timedelta(hours=1)
    SWAGGER_TEMPLATE = {
        "securityDefinitions": {
            "APIKeyHeader": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
            }
        }
    }
    MIGRATIONS_PATH = os.getenv("MIGRATIONS_PATH")


db = SQLAlchemy(session_options={"autoflush": False})
migrate_obj = Migrate()
engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
insp = inspect(engine)

jwt_redis = redis.Redis(
    host=str(os.getenv("REDIS_AUTH_HOST")),
    port=int(os.getenv("REDIS_AUTH_PORT", 6379)),
    password=os.getenv("REDIS_AUTH_PASSWORD"),
    db=0,
    decode_responses=True,
)
jwt = JWTManager()
