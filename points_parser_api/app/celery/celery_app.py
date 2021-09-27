"""
Celery App
"""

from celery.schedules import crontab

from main import celery_app
from app.celery.celery_tasks import task_normalize
from config import Config as conf

scheduler, worker = conf.TASK_QUEUE
celery_app.conf.task_routes = {'app.celery.celery_tasks.task_normalize': {'queue': scheduler},
                               'app.celery.celery_tasks.task_update_outlets_subtask': {'queue': worker},
                               'app.celery.celery_tasks.task_update_metro_stations': {'queue': worker},
                               'app.celery.celery_tasks.task_run_address_normalize': {'queue': worker},
                               'app.celery.celery_tasks.task_run_search_temp_points': {'queue': worker},
                               'app.celery.celery_tasks.task_temp_point_to_base_point': {'queue': worker},

                               }


@celery_app.on_after_configure.connect
def setup_periodic_task_normalize(sender, **kwargs):
    """
    Периодическая задача по нормализации адресов

    :param sender:
    :param kwargs:
    :return: None:
    """

    sender.add_periodic_task(crontab(hour=conf.TASK_NORMALIZE[0],
                                     minute=conf.TASK_NORMALIZE[1],
                                     day_of_month=conf.TASK_NORMALIZE[2]),
                             task_normalize,
                             name='-> Start task_normalize')
