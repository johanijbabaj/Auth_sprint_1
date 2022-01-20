import datetime
import uuid
from typing import Optional

from auth_config import db
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

user_group = db.Table(
    "user_group_rel",
    db.Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    ),
    db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("auth.user.id")),
    db.Column("group_id", UUID(as_uuid=True), db.ForeignKey("auth.group.id")),
    extend_existing=True,
    schema="auth",
)


class User(db.Model):
    """Зарегистрированный в системе пользователь"""

    __table_args__ = {"schema": "auth", "extend_existing": True}
    __tablename__ = "user"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    avatar_link = db.Column(db.String)
    address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    groups = db.relationship(
        "Group", secondary=user_group, lazy="subquery", back_populates="users"
    )

    @property
    def password(self):
        raise AttributeError("Could not get password from password hash")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.login}>"

    def in_group(self, group_id):
        """Проверить, состоит ли пользователь в указанной группе"""
        return self.groups.filter_by(group_id=group_id).first() is not None

    def get_all_groups(self):
        """Список всех групп, в которых состоит пользователь"""
        return self.groups

    def is_admin(self):
        """Состоит ли пользователь в группе администраторов"""
        groups = self.groups
        for g in groups:
            if g.is_admin():
                return True
        return False

    def to_json(self, *, url_prefix: Optional[str] = None):
        """
        Преобразовать запись пользователя в объект для сериализации в Python

        Если задан параметр url_prefix то дополнительно вернуть
        URL для доступа к информации о пользователе, с указанным
        префиксом.
        """
        obj = {"id": self.id, "login": self.login, "email": self.email}
        if url_prefix:
            obj["url"] = f"{url_prefix}/user/account/{self.login}"
        return obj

    def get_history(self, since: Optional[datetime.datetime] = None):
        """
        Вернуть историю действий этого пользователя

        Если задан параметр since, то вернуть только действия, которые
        были позже указанной метки времени
        """
        if since:
            return (
                History.query.filter(History.user_id == self.id)
                .filter(History.timestamp >= since)
                .order_by(History.timestamp.desc())
            )
        else:
            return History.query.filter(History.user_id == self.id).order_by(
                History.timestamp.desc()
            )


class Group(db.Model):
    """Пользовательская группа (роль)"""

    __table_args__ = {"schema": "auth", "extend_existing": True}
    __tablename__ = "group"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)

    users = db.relationship(
        "User", secondary=user_group, lazy="subquery", back_populates="groups"
    )

    def __repr__(self):
        return f"<Group {self.name}>"

    def is_admin(self):
        """Является ли группа группой администраторов"""
        return self.name == "admin"

    def user_in_group(self, user_id):
        """Проверить, состоит ли пользователь в указанной группе"""
        return self.users.filter_by(user_id=user_id).first() is not None

    def get_all_users(self):
        """Список всех пользователей в этой группе"""
        return User.query.filter(User.groups.any(id=self.id))

    def to_json(self, *, url_prefix: Optional[str] = None):
        """
        Преобразовать группу в объект для сериализации в Python

        Если задан параметр url_prefix то дополнительно вернуть
        URL для доступа к информации об указанной группе, с указанным
        префиксом.
        """
        obj = {"id": self.id, "name": self.name, "description": self.description}
        if url_prefix:
            obj["url"] = f"{url_prefix}/group/{self.id}"
        return obj

    @staticmethod
    def from_json(obj):
        """
        Создать группу на основе словаря python
        """
        return Group(
            id=obj["id"],
            name=obj["name"],
            description=obj.get("description", obj["name"]),
        )


class History(db.Model):
    __table_args__ = {"schema": "auth", "extend_existing": True}
    __tablename__ = "history"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("auth.user.id"))
    useragent = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<History {self.useragent}>"

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "useragent": self.useragent,
            "timestamp": self.timestamp.isoformat(),
        }
