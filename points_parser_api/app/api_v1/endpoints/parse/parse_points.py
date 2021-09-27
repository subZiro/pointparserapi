"""
Контролер поиск торговых точек по параметрам
"""

import logging
from flask import g, request
from flask_restplus import Resource

from app import api
from app.errors import bad_request
from app.api_v1.common import ValidateMixin, create_response
from app.api_v1.decorators import manager_required
from app.api_v1.resource_models import parse_search_queries_fields
from config import Config as conf

logger = logging.getLogger('app.api_v1.parse_points')


class ParsePointsAdmCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(ParsePointsAdmCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        _data = request.get_json()
        self.data_flg = self.validate_post_key(_data, ['parser_type', 'search_queries'])
        if self.data_flg:
            self.parser_type = _data['parser_type']
            self.search_queries = _data['search_queries']

    @manager_required
    @api.doc(body=parse_search_queries_fields())
    def post(self):
        """
        Запуск поиска точек.

        хранение в БД найденых записей как TempPoints

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == 'Задание успешно создано!'
        * 'data' - {task_id: str}
        """

        if not self.data_flg:  # проверка корректности введеных данных
            return bad_request(message='Отсутствует обязательное поле или пустое значение')

        if not isinstance(self.search_queries, list):
            return bad_request(message='Ошибка в передаче [search_queries]')

        from app.celery.celery_tasks import task_run_search_temp_points
        task = task_run_search_temp_points.apply_async(args=(self.parser_type, self.search_queries),
                                                       queue=conf.TASK_QUEUE[1],
                                                       priority=0)
        user_ = g.current_user.caption
        logger.debug(f'Пользователь [{user_}], создал задание task_run_search_temp_points, task_id [{task.id}]')
        return create_response(data={'task_id': task.id}, message='Задание успешно создано!')
