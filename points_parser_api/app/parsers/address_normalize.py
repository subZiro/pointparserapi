"""
Нормализация адресов для найденых точек
"""

import os
import logging
import requests

from app import db
from app.models import TempPoint
from app.database import get_address
from app.parsers.parser import get_parser

from config import Config as conf

logger = logging.getLogger('app.parsers.address_normalize')
logger.setLevel(logging.DEBUG)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def run_address_normalize(to_limit: int) -> int:
    """
    Функция по поиску TempPoint без address_id. Лимит обработки внешнего сервиса 1000 в сутки

    :param to_limit: int: количество точек для нормализации
    :return int: количество нормализованных адресов
    """
    log_ = 'run_address_normalize'
    logging.info(f'{log_}. start')
    ok_count = 0

    # получение парсера
    parser = get_parser(parser_type='yandex')
    if parser:
        # не больше тысячи запросов в сутки, согласно бесплатного тарифа
        outlets = db.session.query(TempPoint) \
            .filter(TempPoint.address_id.is_(None), TempPoint.is_checked.isnot(True)) \
            .order_by(TempPoint.pid.desc()) \
            .limit(to_limit)

        for tmp_outlet in outlets:

            if parser.ping:
                adr_id = yandex_get_address(address=tmp_outlet.address)
                if adr_id is not None:
                    tmp_outlet.address_id = adr_id
                    ok_count += 1
                tmp_outlet.is_checked = True
                db.session.commit()

            else:
                # выход по достижении суточного лимита запросов
                logger.info(f'{log_}. Достигнут лимит запросов на текущую дату')
                break

    logging.info(f'{log_}. end. Успешно нормализовано [{ok_count}], адресов')
    return ok_count


def yandex_get_address(address: str = None) -> int or None:
    """
    Функция нормализует заданный адрес через стороннее API
    Документация по Яндекс-API: https://yandex.ru/dev/maps/geocoder/doc/desc/concepts/input_params.html

    :param address: строка для поиска адреса
    :return address_id: int or None: address_id - id нормализованного адреса, None - не удалось найти адрес
    """
    address_id = None
    log_ = 'yandex_get_address'

    url = conf.YANDEX_API_URL.format(conf.YANDEX_API_TOKEN)
    URL_YANDEX_PARSER = f"{url}&format=json&results=1"
    # метод replace не подходит, т.к. если в начале, либо конце строки пристутсвют запятые,
    # заменяющиеся на "+", они оказывают существенное влияние на получаемый результат
    full_address = '+'.join(address.split(','))
    resp = requests.get(f"{URL_YANDEX_PARSER}&geocode={full_address}")
    if resp.status_code == 200:

        data = resp.json()['response']['GeoObjectCollection']['featureMember']
        if data:
            data = data[0]
            metadata = data['GeoObject']['metaDataProperty']['GeocoderMetaData']

            try:
                if metadata['precision'] == 'exact' and metadata['kind'] == 'house':
                    country = metadata['AddressDetails']['Country']
                    region = country['AdministrativeArea']['AdministrativeAreaName']

                    lon, lat = data['GeoObject']['Point']['pos'].split(' ')

                    if 'Locality' in country['AdministrativeArea']:
                        city = country['AdministrativeArea']['Locality'].get("LocalityName")
                        if city is None:
                            city = country['AdministrativeArea']['AdministrativeAreaName']
                    else:
                        city = country['AdministrativeArea']['SubAdministrativeArea']['Locality'].get('LocalityName')
                        if city is None:
                            city = country['AdministrativeArea']['AdministrativeAreaName']
                    # склейка адреса с почтовым индексом
                    caption = metadata['Address'].get('postal_code')
                    caption = caption + ', ' + metadata['text'] if caption else metadata['text']

                    address_id = get_address(
                        address=caption, city=city, region=region, lat=lat, lon=lon, country=country['CountryName'])

            except (KeyError, AttributeError) as err:
                logger.error(f'{log_}. Ошибка получения доступа к данным. ERROR: [{err}]')
        else:
            logger.debug(f'{log_}. Ошибка извлечения данных по ключу [featureMember]')
    else:
        logger.error(f'{log_}. Ошибка сервису. {resp.status_code}')

    if address_id is not None:
        logger.debug(f'{log_}. Нормализован новый адрес. address_id:[{address_id}]')

    return address_id
