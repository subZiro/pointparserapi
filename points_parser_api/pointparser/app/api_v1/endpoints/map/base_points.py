"""
Контролеры раздела "Карты"
"""

from flask import request
from flask_restplus import Resource

from sqlalchemy import and_, func

from app import db, api
from app.models import PointType, Address, BasePoint, PhoneBasePoint, Phone, PointCategory
from app.api_v1.common import ValidateMixin, create_response, prep_search
from app.api_v1.resource_models import post_fields
from app.processing_files import create_excel

from config import Config

LATLNG = Config.LATLNG_REDSQARE


class MapBasePointsCrud(ValidateMixin, Resource):
    """Список координат базовой точки."""

    def __init__(self, *args, **kwargs):
        super(MapBasePointsCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())

        if request.method == "POST":  # post
            self._data = request.get_json()
            self.download = bool(self._data.get('download', False))
            self.type_ids = self._data.get('type_id')
            self.temp_ids = self._data.get('ids')
        elif request.method == "GET":  # get
            pass

    @api.doc(body=post_fields())
    def post(self):
        """
        Получение базовых точек по категориям

        **Описание возвращаемого соощения**
        **При успешном получении массива точек**
        * 'code' == 200
        * 'message' == ""
        * 'data': {'total' - int, количество точек, 'data': [], массив данных по точкам
        """

        filter_fields = {
            'query_id': ('list', PointType.pid),
            'query_name': PointType.caption.ilike,
            # 'type_name': BasePoint.categories.ilike,
            'categories': BasePoint.categories.ilike,
            'city': BasePoint.address.ilike,
        }

        query = db.session.query(
            BasePoint.pid.label('id'),
            BasePoint.caption.label('name'),
            Address.full_address.label('address'),
            func.array_agg(Phone.phone).label('phones'),
            PointType.caption.label('query_name'),
            Address.latitude.label('latitude'),
            Address.longitude.label('longitude'),
        ) \
            .select_from(BasePoint) \
            .join(PointType, PointType.pid == BasePoint.type_id) \
            .join(Address, Address.pid == BasePoint.address_id) \
            .outerjoin(PhoneBasePoint, PhoneBasePoint.point_id == BasePoint.pid) \
            .outerjoin(Phone, Phone.pid == PhoneBasePoint.point_id) \
            .group_by(
            BasePoint.pid, PointType.pid, Address.pid, PointCategory.point_id, Phone.pid, PhoneBasePoint.point_id,
        ) \
            .order_by(BasePoint.pid.desc())

        query = prep_search(query, filter_fields, self._data, {})

        if self.download:
            head = (('ID', 'Название', 'Адрес', 'Телефоны', 'Поисковый запрос', 'Долгота', 'Широта',),)
            filename = 'base_points_map'
            if self.temp_ids is not None:
                query = query.filter(BasePoint.pid.in_(self.temp_ids))
            content = create_excel(filename=filename,
                                   data=list(query),
                                   header=head,
                                   not_send=True)
            data = {'filename': f'{filename}.xlsx', 'content': content}
        else:
            query = query.add_columns(
                PointType.pid.label('query_id'),
                PointType.description.label('query_description'),
            )
            data = {
                'total': query.count(),
                'data': [
                    {'id': x.id,
                     'name': x.name,
                     'address': x.address,
                     'phones': x.phones,
                     'working_times': x.working_times,
                     'query': {'id': x.query_id, 'name': x.query_name},
                     'latlng': [float(x.latitude), float(x.longitude)] if x.longitude and x.latitude else LATLNG,
                     } for x in query]
            }

        return create_response(data=data)

    @api.doc()
    def get(self, idx: int):
        """
        Получение расширеной информации по базовой точке

        **Описание возвращаемого соощения**
        **При успешном получении данных по точке**
        * 'code' == 200
        * 'message' == ""
        * 'data': {}, словарь с данными по точке
        """

        item = db.session.query(
            BasePoint.pid.label('id'),
            BasePoint.caption.label('name'),
            BasePoint.phones,
            BasePoint.working_times,
            BasePoint.address,
            Address.latitude.label('latitude'),
            Address.longitude.label('longitude'),
            BasePoint.categories,
            PointType.pid.label('query_id'),
            PointType.caption.label('query_name')
        ) \
            .select_from(BasePoint) \
            .join(PointType, and_(PointType.pid == BasePoint.type_id, BasePoint.pid == idx)) \
            .join(Address, Address.pid == BasePoint.address_id) \
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
                    'latlng': [float(item.latitude), float(item.longitude)]
                    if item.longitude and item.latitude else LATLNG,
                    'categories': item.categories,
                    'query': {'id': item.query_id, 'name': item.query_name},
                    }
        else:
            data = {}

        return create_response(data=data)
