from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import uuid
from sqlalchemy.dialects.postgresql import UUID
from db import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    avatar_link = db.Column(db.String)
    address = db.Column(db.String)

    def __repr__(self):
        return f'<User {self.login}>'


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Group {self.name}>'


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    useragent = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<History {self.useragent}>'
