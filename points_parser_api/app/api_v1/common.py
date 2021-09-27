"""
Методы работы с api
"""

import re
from datetime import datetime
from enum import Enum

from app import api
from config import Config
from flask import jsonify
from flask_restplus import inputs
from flask_sqlalchemy import BaseQuery
from sqlalchemy import asc, desc, func


def create_response(data=None, code: int = 200, message: str = "") -> jsonify:
    """
    Шаблон ответа для методов АПИ

    :param data: Any
    :param code: int: код ответа
    :param message: str: сообщение
    :return: dict:
    """

    return jsonify(
        {"data": data,
         "code": code,
         "message": message}
    )


def prep_search(query: BaseQuery, fields: dict, args: dict, search_dict: dict) -> BaseQuery:
    """
    Возвращает объект запроса с наложенными фильтрыми

    :param query: BaseQuery: исходный BaseQuery
    :param fields: dict:  возможные полями для фильтрации
    :param args: dict: требуемые поля и ограничения по ним
    :param search_dict: dict: примененые фильтры
    :return: BaseQuery: BaseQuery с фильтрами
    """

    for k, v in args.items():
        if k in fields:
            # применять фильтры только к возможным полям для фильтрации
            if type(fields[k]) == tuple and fields[k][0] == 'equal':
                field = fields[k][1] == v  # {'key': '1'} or {'key': 1} равенство

            elif type(fields[k]) == tuple and fields[k][0] == 'int':
                field = fields[k][1] == int(v)  # {'key': 1} равенство и приведение к типу инт

            elif type(fields[k]) == tuple and fields[k][0] == 'list':
                field = fields[k][1].in_(v)  # {'key': ['1', '2', '3']} or {'key': ['1']}

            elif type(fields[k]) == tuple and fields[k][0] == 'choice':
                # {'key': '1'} or {'key': 1}
                field = fields[k][int(v)]

            elif type(fields[k]) == tuple and fields[k][0] == 'bool':
                # {'is_key': '1'} or {'is_key': 1} or {'is_key': True}, {'is_key': 'true'}
                if not isinstance(v, bool):
                    v = True if v in ('1', 1, 'true', 'True') else False
                field = fields[k][1].is_(v)

            else:
                field = fields[k](f"%{v}%")  # {'key': 'value'} or

            search_dict[k] = v
            query = query.filter(field)

    return query


def sort_by(sort: str):
    """
    Сортировка выборки sort[0] = '+' это asc, '-' это desc. Дефолт desc

    :param sort: str: тип и поле сортировки
    :return:
    """

    return desc(sort[1:]) if sort[0] == '-' else asc(sort[1:])


class ValidateMixin:
    """
    Миксин валидации данных
    """

    def validate_data(self, method_name):
        """

        :param method_name:
        :return:
        """
        types_dict = {
            'str': str,
            'int': int,
            'choices': Enum,
            'date': inputs.date,
            'date_time': self.date_time,
            'lst_of_floats': self.is_it_float,
            'lst_of_integers': self.is_it_int,
        }
        parser = api.parser()
        parser_dict = getattr(self, method_name).__apidoc__.get('params', {})

        for k, v in parser_dict.items():
            if 'type' in v.keys():
                if v['type'] in types_dict.keys():
                    v['type'] = types_dict[v['type']]
            if 'enum' in v.keys():
                v.pop('enum')
            if 'description' in v.keys():
                v.pop('description')
            if 'location' not in v.keys():
                v['location'] = 'args'
            parser.add_argument(k, **v)
        parser.parse_args()

    def validate_post_key(self, json_args, requireds: list or None = None):
        """
        Проверка корректности переданного json метода POST

        :param json_args: dict or None
        :param requireds: list: список обязательных ключей
        :return: bool:
        """

        if not json_args or not isinstance(json_args, dict):
            return False

        requireds = ['offset', 'sort', 'limit'] if requireds is None else requireds
        # проверка обязательных ключей
        for k in requireds:
            if k not in json_args:
                return False
            if (not json_args[k] or not str(json_args[k]).strip()) and str(json_args[k]) != '0':
                return False
        return True

    # noinspection PyMethodMayBeStatic
    def is_it_float(self, values, param_name):
        """

        :param values:
        :param param_name:
        :return:
        """

        if not all([0 <= float(x) <= 1 for x in values.split(',')]):
            raise ValueError('Parameters values must be 0 <= x <= 1')
        return param_name

    # noinspection PyMethodMayBeStatic
    def is_it_int(self, values, param_name):
        """

        :param values:
        :param param_name:
        :return:
        """
        if not all([re.compile(r"(?<![-.])\b[0-9]+\b(?!\.[0-9])").match(x) for x in values.split(',')]):
            raise ValueError('Parameters values must be integers')
        return param_name

    # noinspection PyMethodMayBeStatic
    def date_time(self, value):
        return datetime.strptime(value, Config.DATE_TMPL)
