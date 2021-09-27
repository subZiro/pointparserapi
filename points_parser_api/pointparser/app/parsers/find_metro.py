"""
Парсеры и функции для сторонних API- яндекса
"""

import logging

import requests
from sqlalchemy import and_

from app import db
from app.database import db_add
from app.models import BasePoint, City, PointType, Address
from app.database import get_address
from app.parsers.parser import get_parser
from config import Config as conf

logger = logging.getLogger('app.parsers.find_metro')
logger.setLevel(logging.DEBUG)


def update_metro_stations(city: str, point_type: str, stations: list) -> None:
    """
    Функция ищет станции метро, перечисленные в stantions, через стронний API яндекса

    :param city: str: название города
    :param point_type: str: название типа для поиска
    :param stations: list: название станций
    :return: None
    """
    log_ = 'update_metro_stations'
    logging.info(f'{log_}. Перенос станций метро в БД, запущен')

    city_caption = db.session.query(City.caption).filter(City.caption == city).first()[0]
    point_type = db.session.query(PointType.pid, PointType.caption).filter(PointType.caption == point_type).first()
    # получение парсера
    parser = get_parser(parser_type='yandex')
    if parser:
        if point_type is not None:
            type_id, type_caption = point_type
            all_cnt, ok_cnt = 0, 0
            for line in stations:
                if parser.ping:
                    if yandex_search_geocode_metro(line.strip(), city_caption, type_id, type_caption):
                        logging.info(f'{log_}. Успешно добавлено [{type_caption} {line}]')
                        ok_cnt += 1
                    all_cnt += 1
                else:
                    # выход по достижении суточного лимита запросов
                    logger.info(f'{log_}. Достигнут лимит запросов на текущую дату')
                    break
            logging.info(f'{log_}. Перенос станций метро в БД, завершен. Успешно [{ok_cnt}] из [{all_cnt}]')
        else:
            logging.info(f'{log_}. ERROR: type_caption = [{point_type}] not found in PointType')


def yandex_search_geocode_metro(search_query: str, city: str, type_id: int, type_caption: str) -> bool:
    """
    Поиск и получение метро от яндекса по поисковому запросу

    :param search_query: str: Посковый запрос
    :param city: str: caption модели City
    :param type_id: int: PointType pid
    :param type_caption: str: PointType caption
    :return result: bool: result(bool)
    """
    log_ = 'yandex_search_geocode_metro'
    result = None
    url = conf.YANDEX_API_URL.format(conf.YANDEX_API_TOKEN)
    search_query = city + '+' + type_caption + '+' + search_query.replace(' ', '+')
    param = {
        'lang': 'ru_RU',
        'results': 1,
        'geocode': search_query,
        'format': 'json'
    }

    resp = requests.get(url, params=param)
    if resp.status_code == 200:
        result = False
        data = resp.json()['response']['GeoObjectCollection']['featureMember']
        # проверка, на пустой запрос
        if len(data) == 0:
            return result

        data = data[0]['GeoObject']
        kind = data['metaDataProperty']['GeocoderMetaData']['kind']
        if kind == 'metro':
            caption = data['name']
            base_point = db.session.query(BasePoint) \
                .join(Address, Address.pid == BasePoint.address_id) \
                .join(City, and_(City.pid == Address.city_id, City.caption == city)) \
                .filter(BasePoint.caption == caption) \
                .first()
            if base_point is None:
                try:
                    full_address = data['metaDataProperty']['GeocoderMetaData']['text']
                    lon, lat = data['Point']['pos'].split()
                    data = data['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']
                    country = data['CountryName']
                    # ключи региона могут отсутствовать-не учтено
                    if 'AdministrativeArea' not in data.keys():
                        region = city
                    else:
                        reg_1 = data.get('AdministrativeArea', {}).get('AdministrativeAreaName', {})
                        reg_2 = data.get('AdministrativeArea', {}).get('Locality', {}).get('LocalityName', {})
                        region = reg_1 or reg_2
                    address_id = get_address(address=full_address, city=city, region=region, country=country,
                                             lat=lat, lon=lon)
                    base_point = BasePoint(caption=caption, address_id=address_id, type_id=type_id)
                    result = db_add(base_point)

                # от API яндекса могут прийти ответы с отстутствием ожидаемых ключей
                except (KeyError, AttributeError) as err:
                    result = False
                    logger.error(f"{log_}. Can't get key in data. ERROR: {err}")
        else:
            logger.debug(f"{log_}. 'kind' field in response 'metro 'is not {kind}")
    else:
        logger.error(f"{log_}. Status response is {resp.status_code}")

    return result
