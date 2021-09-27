"""
Модели хранения телефоных номеров
"""

from app import db


class Phone(db.Model):
    """Телефонные номера."""
    __tablename__ = 'tb_phones'
    __table_args__ = {
        'schema': 'common'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)


class PhoneBasePoint(db.Model):
    """Телефонные номера ТТ."""
    __tablename__ = 'tb_phones_base_point'
    __table_args__ = {
        'schema': 'common'
    }
    point_id = db.Column(db.Integer, db.ForeignKey('points.tb_base_points.pid'), primary_key=True)
    phone_id = db.Column(db.BigInteger, db.ForeignKey('common.tb_phones.pid'), primary_key=True)
    is_main = db.Column(db.Boolean, server_default='false')
