"""
Модели управления доступом пользователей
"""

import logging

from datetime import datetime
from flask import current_app

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.exc import BadPayload

from app import db

logger = logging.getLogger('models.authentication')


class UserRole(db.Model):
    """Должности пользователей."""
    __tablename__ = 'tb_user_roles'
    __table_args__ = {
        'schema': 'authentication'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(96), nullable=False, unique=True)
    description = db.Column(db.Text())
    is_default = db.Column(db.Boolean, default=True)


class User(db.Model):
    """Пользователи."""
    __tablename__ = 'tb_users'
    __table_args__ = {
        'schema': 'authentication'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), nullable=False)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('authentication.tb_user_roles.pid'), index=True)
    is_active = db.Column(db.Boolean, default=True)
    caption = db.Column(db.String(64))
    description = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime())

    def __init__(self, **kwargs):
        """
        Конструктор
        """
        super().__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @staticmethod
    def verify_auth_token(token):
        u = db.session.query(User).filter(User.uid == token, User.is_active.is_(True)).first()
        if u is not None:
            u.ping()
            return u
        return None

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': str(self.uid), 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except BadPayload:
            return False

        if data.get('change_email') != str(self.uid):
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    # def is_administrator(self):
    #     return self.role_id == 1

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def update_row(self, data: dict) -> bool:
        """
        Обновление данных пользователя

        :param data: dict: массив с даными для обновления
        :return: bool:
        """

        flg = False
        try:
            [setattr(self, k, v) for k, v in data.items()]
            db.session.commit()
            flg = True
        except Exception as err:
            db.session.rollback()
            logger.error(f'Ошибка обновлени дпнных пользователя. Error: [{err}]')

        return flg
