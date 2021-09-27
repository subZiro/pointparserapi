"""
Модели представления обработаных точек
"""

from app import db


class PointType(db.Model):
    """Модель типов базовых точек в системе"""
    __tablename__ = 'tb_point_types'
    __table_args__ = {
        'schema': 'points'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String)
    is_main = db.Column(db.Boolean, default=False)


class PointSubType(db.Model):
    """Модель типов базовых точек в системе"""
    __tablename__ = 'tb_point_sub_types'
    __table_args__ = {
        'schema': 'points'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(124), nullable=False, unique=True)


class TargetCategory(db.Model):
    """Модель типов базовых точек в системе"""
    __tablename__ = 'tb_target_categories'
    __table_args__ = {
        'schema': 'points'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('points.tb_point_types.pid'), nullable=False, primary_key=True)
    sub_type_id = db.Column(db.Integer, db.ForeignKey('points.tb_point_sub_types.pid'), nullable=False, primary_key=True)


class PointCategory(db.Model):
    """Модель типов базовых точек в системе"""
    __tablename__ = 'tb_point_categories'
    __table_args__ = {
        "schema": 'points',
    }
    point_id = db.Column(db.Integer, db.ForeignKey('points.tb_base_points.pid'), nullable=False, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('points.tb_target_categories.pid'), nullable=False, primary_key=True)


class TempPoint(db.Model):
    """Point, полученый с внешних источников."""
    __tablename__ = 'tb_temp_points'
    __table_args__ = {
        'schema': 'points'
    }
    pid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    address_id = db.Column(db.BigInteger, db.ForeignKey('locations.tb_addresses.pid'), index=True)
    address = db.Column(db.String)
    type_id = db.Column(db.Integer, db.ForeignKey('points.tb_point_types.pid'), index=True)
    caption = db.Column(db.String)  # название
    url = db.Column(db.String)  # url, если есть
    categories = db.Column(db.String)  # категории сложить строкой, разделитель ;
    phones = db.Column(db.String)  # телефоны сложить строкой, разделитель ;
    yandex_id = db.Column(db.String, nullable=False, unique=True)
    working_times = db.Column(db.String)
    type_point = db.Column(db.String)
    lat = db.Column(db.String)
    lon = db.Column(db.String)
    is_checked = db.Column(db.Boolean, default=False)
    email = db.Column(db.String)

    @staticmethod
    def join_cat(data: list or None) -> str:
        """
        Конкатенация списка категорий в строку

        :param data: list or None: список категорий на конкатенацию
        :return result: str строка с категориями
        """
        result = ""
        if data is not None:
            for i in data:
                cat = i.get('class', '')
                cap = i.get('name', '')
                if cap or cat:
                    result += f"{cat or 'неизвестно'}:{cap or 'неизвестно'};"
        return result

    @staticmethod
    def join_phones(data: list or None) -> str:
        """
        Конкатенация списка телефонов в одну строку

        :param data: list or None: список телфонов на конкатенацию
        :return result: str: строка с телефонами
        """
        result = ""
        if data is not None:
            for i in data:
                if i.get('type') == "phone":
                    phone = i.get('formatted')
                    if phone:
                        result += f"{phone};"
        return result


class BasePoint(db.Model):
    """Point, с нормализованным адресом."""
    __tablename__ = 'tb_base_points'
    __table_args__ = {
        "schema": 'points'
    }
    pid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('points.tb_point_types.pid'), index=True, nullable=False)
    address_id = db.Column(db.BigInteger, db.ForeignKey('locations.tb_addresses.pid'), index=True)
    working_times = db.Column(db.String)
    caption = db.Column(db.String(256), nullable=False)
    yandex_id = db.Column(db.String, unique=True)
    is_retail = db.Column(db.Boolean, default=False)

    categories = db.relationship('PointCategory', backref='base_point', uselist=True)
    phones = db.relationship('PhoneBasePoint', backref='base_point', uselist=True)
    address = db.relationship('Address', backref='base_point')
