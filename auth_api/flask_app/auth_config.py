import os
from datetime import timedelta

from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

BASE_PATH = "/v1"


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app=app, session_options={"autoflush": False})
dbschema = "auth,public"
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args={"options": f"-csearch_path={dbschema}"},
)
session = Session(bind=engine)
swagger = Swagger(app)
