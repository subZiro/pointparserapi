"""
Модели представления гео-локаций
"""

from geoalchemy2 import Geometry

from app import db


class City(db.Model):
    """Города."""
    __tablename__ = 'tb_cites'
    __table_args__ = {
        'schema': 'locations'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(96), nullable=False, unique=True)
    code = db.Column(db.String(12), unique=True)
    iso2 = db.Column(db.String(2), unique=True)
    iso3 = db.Column(db.String(3), unique=True)

    address = db.relationship('Address', backref='city', lazy='dynamic')


class Country(db.Model):
    """Страны."""
    __tablename__ = 'tb_countries'
    __table_args__ = {
        'schema': 'locations'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(96), nullable=False, unique=True)
    code = db.Column(db.String(12), unique=True)
    iso2 = db.Column(db.String(2), unique=True)
    iso3 = db.Column(db.String(3), unique=True)
    is_valid = db.Column(db.Boolean, default=True)

    address = db.relationship('Address', backref='country', lazy='dynamic')


class Region(db.Model):
    """Регионы."""
    __tablename__ = 'tb_regions'
    __table_args__ = {
        'schema': 'locations'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caption = db.Column(db.String(96), nullable=False, unique=True)
    code = db.Column(db.String(12), unique=True)
    iso2 = db.Column(db.String(2), unique=True)
    iso3 = db.Column(db.String(3), unique=True)
    is_valid = db.Column(db.Boolean, default=True)

    address = db.relationship('Address', backref='region', lazy='dynamic')


class Address(db.Model):
    """Адрес объекта."""
    __tablename__ = 'tb_addresses'
    __table_args__ = {
        'schema': 'locations'
    }
    pid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    country_id = db.Column(db.Integer, db.ForeignKey('locations.tb_countries.pid'), index=True)
    region_id = db.Column(db.Integer, db.ForeignKey('locations.tb_regions.pid'), index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('locations.tb_cites.pid'), index=True)
    full_address = db.Column(db.String(256))
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    coordinates = db.Column(Geometry(geometry_type='POINT', srid=4326))
    from_coordinates = db.Column(db.Boolean, default=False)
    distance_by_metro = db.Column(db.Float, default=None)  # расстояние до метро
