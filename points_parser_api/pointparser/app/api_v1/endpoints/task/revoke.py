"""
Контролер Мониторинга Celery
"""

import logging

from flask_restplus import Resource

from app import api
from app.errors import not_found, bad_request
from app.api_v1.common import ValidateMixin, create_response

logger = logging.getLogger('app.api_v1.task.revoke')


class TaskRevokeCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(TaskRevokeCrud, self).__init__(*args, **kwargs)

    @api.doc()
    def get(self, task_id: str):
        """
        Остановка выполняемого задания

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == 'Задание успешно task_id остановлено!'
        * 'data' - {task_status: str}
        """

        from app.celery.celery_utils import get_task_status, revoke_task

        if get_task_status(task_id=task_id) is None:
            return not_found(message=f'Задание task_id:[{task_id}], не найдено!')

        if revoke_task(task_id=task_id):
            return create_response(data={}, message=f'Задание task_id: [{task_id}], успешно остановлено!')
        else:
            return bad_request(message=f'Ошибка при попытке остановить задание task_id: [{task_id}]')
