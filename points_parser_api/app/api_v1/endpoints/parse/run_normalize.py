"""
Контролер Нормализации адресов точек
"""

import logging
from flask import g, request
from flask_restplus import Resource

from app import api
from app.api_v1.common import ValidateMixin, create_response
from app.api_v1.decorators import manager_required
from config import Config as conf

logger = logging.getLogger('app.api_v1.normalize.run_normalize')


class RunNormalizeAdmCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(RunNormalizeAdmCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        self.to_limit = int(request.args.get('limit', 0))

    @manager_required
    @api.doc(params={
        'limit': {'description': 'Ограничение по количеству нормализации точек', 'type': 'int', 'default': 500},
    })
    def get(self):
        """
        Запуск нормализация адресов.

        Создание сущностей в Address. Нормализация адресов модели TempPoint, заполнение TempPoint.address_id

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == 'Задание успешно создано!'
        * 'data' - {task_id: str}
        """

        from app.celery.celery_tasks import task_run_address_normalize
        task = task_run_address_normalize.apply_async(args=(self.to_limit,), queue=conf.TASK_QUEUE[1], priority=0)
        user_ = g.current_user.caption
        logger.debug(f'Пользователь [{user_}], создал задание task_run_address_normalize, task_id [{task.id}]')
        return create_response(data={'task_id': task.id}, message='Задание успешно создано!')
