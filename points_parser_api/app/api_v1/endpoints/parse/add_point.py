"""
Контролер добавления точек
"""

import logging
from flask import g, request
from flask_restplus import Resource

from app import api
from app.errors import bad_request
from app.api_v1.common import create_response, ValidateMixin
from app.api_v1.decorators import manager_required
from app.api_v1.resource_models import add_point_fields
from config import Config as conf

logger = logging.getLogger('app.api_v1.add_point')


class AddPointAdmCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(AddPointAdmCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        _data = request.get_json()
        self.data_flg = self.validate_post_key(_data, ['city', 'point_type', 'stations'])
        if self.data_flg:
            self.city = _data['city']
            self.point_type = _data['point_type']
            self.stations = _data['stations']

    @manager_required
    @api.doc(body=add_point_fields())
    def post(self):
        """
        Добавление новых базовых точек.

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == 'Задание успешно создано!'
        * 'data' - {task_id: str}
        """

        if not self.data_flg:
            return bad_request(message='Отсутствует обязательное поле или пустое значение')

        if not isinstance(self.stations, list):
            return bad_request(message='Ошибка в передаче [stations]')

        from app.celery.celery_tasks import task_update_metro_stations
        task = task_update_metro_stations.apply_async(args=(self.city, self.point_type, self.stations),
                                                      queue=conf.TASK_QUEUE[1],
                                                      priority=0)

        user_ = g.current_user.caption
        logger.debug(f'Пользователь [{user_}], создал задание update_metro_stations, task_id [{task.id}]')
        return create_response(data={'task_id': task.id}, message='Задание успешно создано!')
