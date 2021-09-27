"""
Контролер обновления БД/перенос из точек TempPoints в BasePoints
"""

import logging
from flask import g, request
from flask_restplus import Resource

from app import api
from app.api_v1.common import ValidateMixin, create_response
from app.api_v1.decorators import manager_required
from config import Config as conf

logger = logging.getLogger('app.api_v1.refresh_base_points')


class RefreshPointsAdmCrud(ValidateMixin, Resource):

    def __init__(self, *args, **kwargs):
        super(RefreshPointsAdmCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        self.point_type = request.args.get('point_type')

    @manager_required
    @api.doc(params={
        'point_type': {'description': 'название переносимого типа точек', 'type': 'str', 'default': 'торговая точка'},
    })
    def get(self):
        """
        Перенос из TempPoints в BasePoints.

        Параметром point_type задается название переносимого типа точек

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == 'Задание успешно создано!'
        * 'data' - {task_id: str}
        """

        from app.celery.celery_tasks import task_temp_point_to_base_point
        task = task_temp_point_to_base_point.apply_async(args=(self.point_type,),
                                                         queue=conf.TASK_QUEUE[1],
                                                         priority=0)
        user_ = g.current_user.caption
        logger.debug(f'Пользователь [{user_}], создал задание temp_point_to_base_point, task_id [{task.id}]')
        return create_response(data={'task_id': task.id}, message='Задание успешно создано!')
