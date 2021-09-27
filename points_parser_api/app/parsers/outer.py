"""
Методы обработки БД, после парсинга точек/метро и тд.
"""

import logging

from sqlalchemy import and_

from app import db
from app.models import BasePoint, Phone, PhoneBasePoint, PointCategory, PointType, TempPoint, TargetCategory
from app.database import db_add
from app.database import get_item

logger = logging.getLogger('app.parsers.outer')
logger.setLevel(logging.DEBUG)


def process_phones(source: str) -> list:
    """
    Функция создает сущности PhoneBasePoint из строки запроса
    :param source: Строка с параметрами
    :return: возвращает список созданных в сесси сущностей
    """
    res = []
    phones = set()

    if source:

        for i in source.split(";"):
            if i:
                p = "".join(j for j in i if j.isdigit())

                phone = db.session.query(Phone).filter(Phone.phone == p).first()
                if phone is None:
                    phone = Phone(phone=p)
                    db.session.add(phone)
                    db.session.commit()

                phones.add(phone.pid)

        for phone_id in phones:
            res.append(PhoneBasePoint(phone_id=phone_id))

    return res


def process_categories(source: str) -> list:
    """
    Функция создает сущности PointCategory из строки запроса
    :param source: Строка с параметрами
    :return: возвращает список созданных в сесси сущностей
    """
    res = []

    for i in source.split(";"):
        data = i.split(':')
        if len(data) == 2:
            the_type, sub_type = data
            type_id = get_item(the_type, "point_types")
            sub_type_id = get_item(sub_type, "point_sub_types")

            category = db.session.query(TargetCategory) \
                .filter(TargetCategory.type_id == type_id, TargetCategory.sub_type_id == sub_type_id) \
                .first()

            if category is None:
                category = TargetCategory(type_id=type_id, sub_type_id=sub_type_id)
                db.session.add(category)
                db.session.commit()

            res.append(PointCategory(category_id=category.pid))

    return res


def temp_point_to_base_point(caption) -> None:
    """
    Перенос данных из модели TempPoint в модель BasePoint.

    :param caption: Название модели PointType для переноса из TempPoint в базоыве точки
    :return None:
    """
    log_ = 'temp_point_to_base_point'
    logger.info(f"{log_}. processing for caption: {caption}. start")
    temp_points = db.session.query(TempPoint) \
        .join(PointType, and_(PointType.pid == TempPoint.type_id, PointType.caption == caption)) \
        .filter(TempPoint.address_id.isnot(None))

    for temp in temp_points:

        base_point = db.session.query(BasePoint).filter(BasePoint.yandex_id == temp.yandex_id).first()
        if base_point is None:
            new_base_point = BasePoint(type_id=temp.type_id,
                                       address_id=temp.address_id,
                                       working_times=temp.working_times,
                                       caption=temp.caption,
                                       yandex_id=temp.yandex_id)

            for c in process_categories(temp.categories):
                new_base_point.categories.append(c)

            for p in process_phones(temp.phones):
                new_base_point.phones.append(p)

            db_add(new_base_point)
    logger.info(f'{log_}. processing for caption: {caption}. end')


def temp_point_process_categories() -> None:
    """
    Заполнение категорий из TempPoint.

    :return None:
    """
    log_ = 'temp_point_process_categories'
    logger.info(f"{log_}. processing. start")

    for cat in db.session.query(TempPoint.categories):  # итерации по точкам
        for i in cat[0].split(";"):  # итерации по категориям
            data = i.split(':')
            if len(data) == 2:
                the_type, sub_type = data
                type_id = get_item(the_type, "point_types")
                sub_type_id = get_item(sub_type, "point_sub_types")

                category = db.session.query(TargetCategory) \
                    .filter(TargetCategory.type_id == type_id, TargetCategory.sub_type_id == sub_type_id) \
                    .first()
                if category is None:
                    category = TargetCategory(type_id=type_id, sub_type_id=sub_type_id)
                    db_add(category)

    logger.info(f'{log_}. processing. end')
