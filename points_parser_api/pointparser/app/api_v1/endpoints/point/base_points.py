"""
Контролеры раздела "Точки продаж"
"""

from flask import request
from flask_restplus import Resource
from sqlalchemy import func

from app import api, db
from app.models import BasePoint, Address, Country, Region, City, Phone, PhoneBasePoint, PointType
from app.errors import bad_request
from app.api_v1.common import ValidateMixin, create_response, prep_search, sort_by
from app.processing_files import create_excel
from app.api_v1.resource_models import post_fields


def get_basepoints_fields() -> dict:
    """
    Словарь с возможными фильтрами к разделу точки

    :return: dict:
    """

    return {
        'name': BasePoint.caption.ilike,
        'is_retail': ('bool', BasePoint.is_retail),
        'type_id': ('list', BasePoint.type_id),
        'phone': ('equal', Phone.phone),
        'city': City.caption.ilike,
        'country': Country.caption.ilike,
        'region': Region.caption.ilike,
        'address': Address.full_address.ilike,
    }


class BasePointsCrud(ValidateMixin, Resource):
    """Точки."""

    def __init__(self, *args, **kwargs):
        super(BasePointsCrud, self).__init__(*args, **kwargs)
        self.validate_data(request.method.lower())
        self.data_flg = self.validate_post_key(request.get_json(), ['offset', 'limit', 'sort'])
        _data = request.get_json()
        if self.data_flg:
            self.offset = int(_data['offset'])
            self.limit = int(_data['limit'])
            self.sort = _data['sort']
            self.download = bool(_data.get('download', False))
            self.filters = _data.get('filter', dict())

    @api.doc(body=post_fields())
    def post(self):
        """
        Список торговых точек в системе.

        **Описание возвращаемого соощения**
        **При успешном получении массива документов**
        * 'code' == 200
        * 'message' == ""
        * 'data' == {'limit': int, offset': int, 'total': int, 'data': list(Список торговых точек в системе)}
        """

        if not self.data_flg:  # проверка корректности введеных данных
            return bad_request(message='Отсутствует обязательное поле или пустое значение')

        search = {}
        query = db.session.query(
            BasePoint.pid.label('id'),
            BasePoint.caption.label('name'),
            BasePoint.categories,
            PointType.caption.label('type_name'),
            BasePoint.is_retail,
            BasePoint.working_times,
            func.array_agg(Phone.phone).label('phones'),
            Address.full_address.label('full_address'),
            City.caption.label('city'),
            Region.caption.label('region'),
            Country.caption.label('country'),
        ) \
            .select_from(BasePoint) \
            .join(Address, Address.pid == BasePoint.address_id) \
            .join(Region, Region.pid == Address.region_id) \
            .join(Country, Country.pid == Address.country_id) \
            .join(City, City.pid == Address.city_id) \
            .outerjoin(PhoneBasePoint, PhoneBasePoint.point_id == BasePoint.pid) \
            .outerjoin(Phone, Phone.pid == PhoneBasePoint.phone_id) \
            .outerjoin(PointType, PointType.pid == BasePoint.type_id) \
            .order_by(sort_by(self.sort))
        query = prep_search(query, get_basepoints_fields(), self.filters, search)

        if self.download:
            query = query.add_columns(
                BasePoint.type_id,
                PointType.description.label('type_description'),
            )
            head = (('ID', 'Название' 'Категория', 'Тип', 'Сеть', 'Время работы', 'Телефоны',
                     'Адресс', 'Город', 'Регион', 'Страна',),)
            filename = 'base_points'
            content = create_excel(filename=filename, data=list(query), header=head, not_send=True)
            data = {'filename': f'{filename}.xlsx', 'content': content}
        else:
            data = {'offset': self.offset,
                    'limit': self.limit,
                    'total': query.count(),
                    'data': [
                        {'id': x.id,
                         'name': x.name,
                         'working_times': x.working_times,
                         'is_retail': x.is_retail,
                         'type': {'id': x.type_id,
                                  'name': x.type_description,
                                  'description': x.type_description,
                                  },
                         'categories': x.categories,
                         'country': x.country,
                         'region': x.region,
                         'city': x.city,
                         'full_address': x.full_address,
                         'phones': x.phones if x.phones else None,
                         } for x in query.offset(self.offset).limit(self.limit)],
                    }

        return create_response(data=data)
