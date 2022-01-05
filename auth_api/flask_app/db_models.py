import uuid
from sqlalchemy.dialects.postgresql import UUID
from auth_config import db


class User(db.Model):
    """Зарегистрированный в системе пользователь"""

    __tablename__ = 'user'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    avatar_link = db.Column(db.String)
    address = db.Column(db.String)

    groups = db.relationship(
        'UserGroup',
        backref=db.backref('user', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.login}>'

    def in_group(self, group_id):
        """Проверить, состоит ли пользователь в указанной группе"""
        return self.groups.filter_by(group_id=group_id).first() is not None

    def get_all_groups(self):
        """Список всех групп, в которых состоит пользователь"""
        return Group.query.join(
            UserGroup, UserGroup.group_id == Group.id
        ).filter(UserGroup.used_id == self.id)


class Group(db.Model):
    """Пользовательская группа (роль)"""

    __tablename__ = 'group'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)

    users = db.relationship(
        'UserGroup',
        backref=db.backref('group', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Group {self.name}>'

    def user_in_group(self, user_id):
        """Проверить, состоит ли пользователь в указанной группе"""
        return self.users.filter_by(user_id=user_id).first() is not None

    def get_all_users(self):
        """Список всех пользователей в этой группе"""
        return User.query.join(
            UserGroup, UserGroup.user_id == User.id
        ).filter(UserGroup.group_id == self.id)


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    useragent = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<History {self.useragent}>'


class UserGroup(db.Model):
    """Членство пользователя в группе"""
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group.id'))
