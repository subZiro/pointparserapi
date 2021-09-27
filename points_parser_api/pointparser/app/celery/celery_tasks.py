"""
Задачи Celery
"""

import logging
from celery import shared_task

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.celery.celery_tasks')


@shared_task()
def task_run_search_temp_points(parser_type: str, query_rows: list):
    """
    Поиск точек по поисковым запросам

    :return: str: message: сообщение о выполнении задачи
    """
    logger.debug(f'run_search_temp_points start')
    from app.parsers.find_points import run_search_temp_points
    flg = run_search_temp_points(parser_type=parser_type, query_rows=query_rows)
    logger.debug(f'run_search_temp_points end')
    return 'Search temp points is completed!' if flg else 'Search temp points is failed!'


@shared_task()
def task_run_address_normalize(to_limit: int):
    """
    Нормализация адресов Точек

    :return: str: message: сообщение о выполнении задачи
    """
    logger.debug(f'run_address_normalize start')
    from app.parsers.address_normalize import run_address_normalize
    cnt = run_address_normalize(to_limit=to_limit)
    logger.debug(f'run_address_normalize end')
    return f'Address normalize completed successfully for [{cnt}]'


@shared_task(time_limit=7200)
def task_normalize():
    """
    Периодическое задание нормализация адресов Точек

    :return: str: message: сообщение о выполнении задачи
    """
    to_limit = 1000
    flg = False

    from flask import current_app
    stage = current_app.config['ENV']
    msg = f'Address normalize not start in stage {stage}'

    if stage == 'production':
        if flg:
            logger.debug('run_address_normalize. start')
            from app.parsers.address_normalize import run_address_normalize
            cnt = run_address_normalize(to_limit=to_limit)
            msg = f'Address normalize completed successfully for [{cnt}]'
            logger.debug('run_address_normalize. end')
        else:
            logger.debug('run_address_normalize. skipped')
            msg = f'Address normalize not start. flg = {flg}'
    else:
        logger.debug(f'run_address_normalize. not available for {current_app.config["ENV"]}')

    return msg


@shared_task()
def task_update_metro_stations(city: str, point_type: str, stations: list):
    """
    Поиск станций метро

    :return: str: message: сообщение о выполнении задачи
    """
    logger.debug(f'update_metro_stations start')
    from app.parsers.find_metro import update_metro_stations
    update_metro_stations(city=city, point_type=point_type, stations=stations)
    logger.debug(f'update_metro_stations end')
    return f'update metro stations completed successfully for [{city, point_type}]'


@shared_task()
def task_temp_point_to_base_point(point_type: str):
    """
    Задание перенос точек из TempPoints в BasePoints

    :return: str: message: сообщение о выполнении задачи
    """
    logger.debug(f'temp_point_to_base_point start')
    from app.parsers.outer import temp_point_to_base_point
    temp_point_to_base_point(caption=point_type)
    logger.debug(f'temp_point_to_base_point end')
    return f'TempPoint to BasePoint completed successfully for [{point_type}]'
