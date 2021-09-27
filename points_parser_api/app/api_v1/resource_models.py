"""
Методы моделей шаблонов пост запросов
"""

from flask_restplus import fields
from app import api


def user_create_update_field():
    """
    Общий набор полей для создания/обновления пользователей

    :return: dict
    """

    return {
        'email': fields.String(description='Почта пользователя', example=None, required=False),
        'role_id': fields.Integer(description='id роли пользователя', example=None, required=False),
        'is_active': fields.Boolean(description='Статус активности пользователя', example=True, required=False),
        'caption': fields.String(description='Название аккаунта', example=None, required=False),
        'description': fields.String(description='Описание аккаунта', example=None, required=False),
    }


def user_create_fields():
    """
    Модель fields для post запроса создания нового пользователя.
    """
    return api.model('Resource_user_create', user_create_update_field())


def user_update_fields():
    """
    Модель fields для post запроса изменения данных пользователя.
    """
    user_update = user_create_update_field()
    user_update['user_id'] = fields.Integer(description='ID пользователя', example=None, required=True)
    return api.model('Resource_user_update', user_update)


def post_fields():
    """
    Модель fields для post запроса с обязательными полями.
    """

    return api.model(
        'Resource_post',
        {'limit': fields.Integer(description='Максимальное количество элементов в ответе', example=40, required=True),
         'offset': fields.Integer(description='Смещение по выборке', example=0, required=True),
         'sort': fields.String(description='Сортировка элемантов по (- asc, + desc)', example='-key', required=True),
         'filter': fields.Raw(description='Словарь применяемых фильтров', example={}, required=False),
         },
    )


def add_point_fields():
    """
    Модель fields для post запроса добавления точек.

    Пример json:
    {
        "city": str, // город
        "point_type": str, // тип точки
        "stations": list, // поисковые запросы
    }
    """
    return api.model(
        'Resource_add_points',
        {'city': fields.String(description='Город поиска', example='Москва', required=True),
         'point_type': fields.String(description='Тип Базовой точки', example='metro', required=True),
         'stations': fields.List(fields.String(example='Станция метро'),
                                 description='Список (Станции)',
                                 required=True),
         },
    )


def parse_search_queries_fields():
    """
    Модель fields для post запроса поиска точек.

    Пример json:
    {
        "parser_type": str, // тип парсера
        "search_queries": list, // поисковые запросы
    }
    """
    return api.model(
        'Resource_parse_search_queries',
        {'parser_type': fields.Integer(description='Тип парсера', example='yandex', required=True),
         'search_queries': fields.List(fields.String(example='Пример запроса, торговая точка'),
                                       description='Список (Поисковые запросы, Тип искомой точки)',
                                       required=True),
         },
    )
