"""
Контролеры раздела "Карты"
"""

from flask import request
from flask_restplus import Resource

from sqlalchemy import and_

from app import db, api
from app.models import PointType, TempPoint
from app.processing_files import create_excel
from app.api_v1.common import ValidateMixin, create_response, prep_search
from app.api_v1.resource_models import post_fields

from config import Config

LATLNG = Config.LATLNG_REDSQARE


class MapTempPointsCrud(ValidateMixin, Resource):
    """Список координат временной точки."""

    def __init__(self, *args, **kwargs):
        super(MapTempPointsCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())

        if request.method == "POST":  # post
            self._data = request.get_json()
            self.download = bool(self._data.get('download', 0))
            self.type_ids = self._data.get('type_id')
            self.temp_ids = self._data.get('ids')
        elif request.method == "GET":  # get
            pass

    @api.doc(body=post_fields())
    def post(self):
        """
        Получение временных точек

        **Описание возвращаемого соощения**
        **При успешном получении массива точек**
        * 'code' == 200
        * 'message' == ""
        * 'data': {'total' - int, количество точек, 'data': [], массив данных по точкам
        """

        filter_fields = {
            'query_id': ('list', PointType.pid),
            'query_name': PointType.caption.ilike,
            'categories': TempPoint.categories.ilike,
            'city': TempPoint.address.ilike,
        }

        query = db.session.query(
            TempPoint.pid.label('id'),
            TempPoint.caption.label('name'),
            TempPoint.address,
            TempPoint.categories,
            TempPoint.lat.label('latitude'),
            TempPoint.lon.label('longitude'),
        ) \
            .select_from(TempPoint) \
            .order_by(TempPoint.pid.desc())

        query = prep_search(query, filter_fields, self._data, {})

        if self.download:
            head = (('ID', 'Название', 'Адрес', 'Категории', 'Долгота', 'Широта',),)
            filename = 'temp_points_map'
            if self.temp_ids is not None:
                query = query.filter(TempPoint.pid.in_(self.temp_ids))
            content = create_excel(filename=filename,
                                   data=list(query),
                                   header=head,
                                   not_send=True)
            data = {'filename': f'{filename}.xlsx', 'content': content}
        else:
            data = {
                'total': query.count(),
                'data': [
                    {'id': x.id,
                     'name': x.name,
                     'address': x.address,
                     'categories': x.categories,
                     'latlng': [float(x.latitude), float(x.longitude)] if x.longitude and x.latitude else LATLNG,
                     } for x in query]
            }

        return create_response(data=data)

    @api.doc()
    def get(self, idx: int):
        """
        Получение информации по базовой точке

        **Описание возвращаемого соощения**
        **При успешном получении данных по точке**
        * 'code' == 200
        * 'message' == ""
        * 'data': {}, словарь с данными по точке
        """

        item = db.session.query(
            TempPoint.pid.label('id'),
            TempPoint.caption.label('name'),
            TempPoint.url,
            TempPoint.email,
            TempPoint.phones,
            TempPoint.working_times,
            TempPoint.address,
            TempPoint.is_checked,
            TempPoint.categories,
        ) \
            .select_from(TempPoint) \
            .join(PointType, and_(PointType.pid == TempPoint.type_id, TempPoint.pid == idx)) \
            .first()

        if item is not None:
            data = {'id': item.id,
                    'name': item.name,
                    'url': item.url,
                    'email': item.email,
                    'phones': item.phones,
                    'working_times': item.working_times,
                    'address': item.address,
                    'is_checked': item.is_checked,
                    'latlng': [float(item.latitude),
                               float(item.longitude)] if item.longitude and item.latitude else LATLNG,
                    'categories': item.categories,
                    }
        else:
            data = {}

        return create_response(data=data)
