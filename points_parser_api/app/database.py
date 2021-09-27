"""
Взаимодействие с БД
"""

import logging

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Region, Country, Address, PointType, PointSubType, City

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.database')


def db_add(row: BaseQuery) -> bool:
    """
    Метод создания сохранения обновленной модели БД

    :param row: BaseQuery: обновляемый объект
    :return is_rslt: bool: результат создания сохранения в БД
    """

    flg = False
    try:
        db.session.add(row)
        db.session.commit()
    except SQLAlchemyError as err:
        db.session.rollback()
        logger.error(f'Ошибка обновления данных. ERROR: {err}')
    else:
        flg = True

    return flg


def db_add_all(rows: list) -> bool:
    """
    Метод создания новых/обновления существующих моделей БД

    :param rows: list: список обновляемых объектов
    :return is_rslt: bool: результат создания записи в БД
    """

    flg = False
    try:
        db.session.add_all(rows)
        db.session.commit()
    except SQLAlchemyError as err:
        db.session.rollback()
        logger.error(f'Ошибка обновления данных. ERROR: {err}')
    else:
        flg = True
        logger.debug(f"В БД изменено/сохраненно [{len(rows)}], записей")

    return flg


def db_delete(obj) -> bool:
    """
    Метод удаления объекта из БД

    :param obj: удаляемый оъект из БД
    :return is_rslt: bool: результат удаления из БД
    """

    flg = False
    try:
        db.session.delete(obj)
        db.session.commit()
    except SQLAlchemyError as err:
        db.session.rollback()
        logger.error(f'Ошибка обновления данных. ERROR: {err}')
    else:
        flg = True

    return flg


TYPES_MODEL = {
    'city': City,
    'region': Region,
    'country': Country,
    'point_types': PointType,
    'point_sub_types': PointSubType,
}


def get_item(caption: str, the_type: str) -> int or None:
    """
    Получение pid модели the_type по ее caption, если такой записи не существует создание новой

    :param caption: str: значение
    :param the_type: str: ключ TYPES_MODEL
    :return: int or None:
    """
    model = TYPES_MODEL[the_type]

    if caption:
        caption = caption.strip()
        caption = caption if caption != '[not set]' else 'не задано'
        item = db.session.query(model).filter(model.caption == caption).first()
        if not item:
            item = model(caption=caption)
            db.session.add(item)
            db.session.commit()
        return item.pid

    return None


def get_address(address: str, city: str, region: str, country: str, lat: str or None, lon: str or None,
                from_coordinates: bool = None, distance_by_metro: float = None) -> int or None:
    """
    Получение индификатора адреса

    :param address: str:
    :param city: str:
    :param region: str:
    :param country: str:
    :param lat: str or None:
    :param lon: str or None:
    :param from_coordinates: bool or None:
    :param distance_by_metro: float or None:
    :return: int or None:
    """
    if all((city, region, country)):
        city_id = get_item(city, 'city')
        region_id = get_item(region, 'region')
        country_id = get_item(country, 'country')

        loc = db.session.query(Address) \
            .filter_by(country_id=country_id, region_id=region_id, city_id=city_id, full_address=address) \
            .first()

        if not loc:
            loc = Address(
                country_id=country_id,
                region_id=region_id,
                city_id=city_id,
                full_address=address,
                latitude=(lat or None),
                longitude=(lon or None),
                coordinates=func.ST_SetSRID(func.ST_MakePoint(float(lon), float(lat)), 4326) if lat and lon else None,
                from_coordinates=from_coordinates or None,
                distance_by_metro=distance_by_metro or 0
            )
            db.session.add(loc)
            db.session.commit()

        return loc.pid

    return None
