"""
Контролер Мониторинга Celery
"""

import logging

from flask_restplus import Resource

from app import api
from app.errors import not_found
from app.api_v1.common import ValidateMixin, create_response

logger = logging.getLogger('app.api_v1.task.status')


class TaskStatusCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(TaskStatusCrud, self).__init__(*args, **kwargs)

    @api.doc()
    def get(self, task_id: str):
        """
        Проверка статуса выполняемого задания

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == ''
        * 'data' - {task_status: str}
        """

        from app.celery.celery_utils import get_task_status
        status = get_task_status(task_id)
        msg = f'Задание task_id:[{task_id}], не найдено!'
        return create_response(data={'task_status': status}) if status is not None else not_found(message=msg)
