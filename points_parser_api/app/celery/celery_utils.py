"""
Utils for Celery application
"""
import logging
from time import sleep
from celery.result import AsyncResult
from main import celery_app

logger = logging.getLogger('app.celery.utils')


def wait_end_tasks(tasks: list, time_step: int = 15) -> None:
    """
    Метод проверяет завершение выполнения списка задач

    :param tasks: список заданий
    :param time_step: int: ожидание перед повторным опросом задач
    :return: None
    """

    time_limit = 7200  # запасной выход из цикла 2 часа на все под задачи
    time_run = 0

    while True:
        for i, task in enumerate(tasks):
            if get_task_status(task) in ['SUCCESS', 'FAILURE', 'REVOKED']:
                tasks.pop(i)
        if len(tasks) == 0:  # закончились задачи
            break
        if time_run >= time_limit:  # вышло время, остановка всех задач
            [revoke_task(task_id=task) for task in tasks]
            logger.debug(f'wait_end_tasks. Limit run time task. revoked tasks:[{tasks}]')
            break

        time_run += time_step
        sleep(time_step)
    return None


def get_task_status(task_id: str) -> str:
    """
    Получение статуса задачи

    :param task_id: str: id задания
    :return result: str: статус задания
    """

    try:
        result = AsyncResult(task_id).state
    except Exception as err:
        result = None
        logger.error(f'get_task_status. Задание: [{task_id}] не найдено. Error: [{err}]')

    return result


def revoke_task(task_id: str) -> bool:
    """
    Отмена задачи

    :param task_id: str: id задания
    :return result: bool: true - успешная отмена
    """

    try:
        celery_app.control.revoke(task_id, terminate=True)
        result = True
        logger.info(f'revoke_task. Задание: [{task_id}]. Успешно остановлено!')
    except Exception as err:
        result = False
        logger.error(f'revoke_task. Ошибка остановки задания: [{task_id}]. Error: [{err}]')

    return result
