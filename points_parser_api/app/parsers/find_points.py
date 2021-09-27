"""
Парсеры и функции для сторонних API- яндекса
"""

import logging
import os

import requests
from time import sleep

from app import db
from app.database import db_add, db_add_all
from app.models import TempPoint, BasePoint, ParserDetail, SearchHistory
from app.database import get_item
from app.processing_files import create_excel
from app.parsers.parser import get_parser
from config import Config as conf

logger = logging.getLogger('app.parsers.find_points')
logger.setLevel(logging.DEBUG)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def save_points_to_excel(filename: str, max_pid: int) -> None:
    """
    Сохранение результатов в excel

    :param filename: str: файл сохранения документа
    :param max_pid: int: крайний id TempPoint
    :return: None
    """
    head = (('pid', 'addres_id', 'caption', 'url', 'categories', 'phones', 'yandex_id', 'working_times', 'lat', 'lon',
             'valid_address_id', 'address', 'is_checked', 'type_id', 'type_point', 'email',),)
    query = db.session.query(
        TempPoint.pid, TempPoint.address_id, TempPoint.caption, TempPoint.url, TempPoint.categories,
        TempPoint.phones, TempPoint.yandex_id, TempPoint.working_times, TempPoint.lat, TempPoint.lon,
        TempPoint.valid_address_id, TempPoint.address, TempPoint.is_checked, TempPoint.type_id,
        TempPoint.type_point, TempPoint.email
    ) \
        .filter(TempPoint.pid > max_pid)
    filename = f"{BASEDIR}/files/{filename.replace(' ', '_')}.xlsx"
    create_excel(filename=filename, data=list(query.all()), header=head, not_send=True, to_save=True)
    logger.debug('save_points_to_excel. Результаты поиска успешно сохранены в excel')


def run_search_temp_points(parser_type: str, query_rows: list) -> bool:
    """
    Сохраняет в базу данных объекты из поиска через API yandex

    :param parser_type: str: Название парсера в ParserDetail
    :param query_rows: list: Список поискавых запросов
    :return: bool: true - поиск выполнен иначе false
    """
    log_ = 'run_search_temp_points'
    logger.info(f'{log_}. start')
    type_model = 'point_types'

    # получение парсера
    parser = get_parser(parser_type=parser_type)
    if parser:
        for row in query_rows:
            search_query, type_caption = row.split(',')
            search_query = search_query.strip()
            type_capt = type_caption.strip()
            # сохранение истории запросов
            history = db.session.query(SearchHistory) \
                .filter_by(parser_id=parser.pid, search_query=search_query) \
                .first()
            if history is None:
                history = SearchHistory(parser_id=parser.pid, search_query=search_query, cnt_results=0, skip=0)
                db_add(history)

            if history.is_complete is True:
                continue
            else:
                if parser.ping:
                    max_pid = db.session.query(TempPoint.pid).order_by(TempPoint.pid.desc()).first()
                    max_pid = max_pid[0] if max_pid is not None else 0
                    yandex_search_points(history=history, parser=parser, type_caption=type_capt, type_model=type_model)
                    save_points_to_excel(filename=search_query, max_pid=max_pid)
                    logger.info(f'{log_}. pause 2 min')
                    sleep(120)
                else:
                    # выход по достижении суточного лимита запросов
                    logger.info(f'{log_}. Достигнут лимит запросов на текущую дату')
                    break

    logger.info(f'{log_}. end')
    return True


def yandex_search_points(history: SearchHistory, parser: ParserDetail, type_caption: str,
                         type_model: str = "outlet", type_search: str = 'biz') -> None:
    """
    Поиск и получение магазинов и др. сущностей от яндекса по поисковому запросу.
    Сохранение в БД, модель TempPoint.

    :param history: str: История запросов. модель SearchHistory
    :param parser: str: Используемый парсер. Название см в БД: модель ParserDetail
    :param type_caption: str: Тип(описание) точки- магазин, детский садик и тп
    :param type_model: str: Тип получаемой сущности, default = outlet
    :param type_search: str: Тип поискового запроса, default = biz. См документацию (parsers.tb_parsers_limit)
    :return: None
    """
    log_ = 'yandex_search_points'
    logger.info(f'{log_}. processing for search query: [{history.search_query}]. start')

    url = conf.SEARCH_MAP_URL
    token = conf.SEARCH_MAP_TOKEN
    max_result = 500

    skip = history.skip
    cnt_results = history.cnt_results
    search_query = history.search_query

    type_id = get_item(caption=type_caption, the_type=type_model)

    while parser.ping:
        resp = requests.get(url, params={"apikey": token,
                                         "lang": 'ru_RU',
                                         "skip": (skip * max_result),
                                         "results": max_result,
                                         'type': type_search,
                                         "text": search_query
                                         })

        if resp.status_code == 200:
            skip += 1
            history.skip = skip
            db.session.commit()

            data = resp.json()['features']
            logger.info(f'{log_}. От сервиса получено [{len(data)}] записей')
            temp_outlets = []
            for item in data:
                metadata = item["properties"]["CompanyMetaData"]
                if db.session.query(TempPoint).filter_by(yandex_id=metadata["id"]).first() is None and \
                        db.session.query(BasePoint).filter_by(yandex_id=metadata["id"]).first() is None:
                    phones = metadata.get("Phones")
                    categories = metadata.get("Categories")
                    lat_lon = item['geometry']["coordinates"]
                    temp_outlet = TempPoint(caption=item["properties"]["name"],
                                            yandex_id=metadata["id"],
                                            address=metadata["address"],
                                            url=metadata.get("url"),
                                            lat=lat_lon[1],
                                            lon=lat_lon[0],
                                            type_point=type_caption,
                                            phones=TempPoint.join_phones(phones) if phones else "",
                                            categories=TempPoint.join_cat(categories) if categories else "",
                                            working_times=metadata.get("Hours", {}).get("text"),
                                            type_id=type_id,
                                            )
                    temp_outlets.append(temp_outlet)

            cnt_results += len(temp_outlets)
            db_add_all(temp_outlets)

            # максимальный лимит результатов в запросе 500. Если меньше 500, значит получены все ТТ
            if len(data) < max_result:
                history.is_complete = True
                db.session.commit()
                logger.info(f'{log_}. По запросу [{search_query}], получены все записи')
                break

        else:
            logger.info(f'{log_}. Сервис недоступен! Код ответа [{resp.status_code}]')
            break

    history.cnt_results = cnt_results
    db.session.commit()

    logger.info(f'{log_}. processing for search query: [{history.search_query}]. end')
