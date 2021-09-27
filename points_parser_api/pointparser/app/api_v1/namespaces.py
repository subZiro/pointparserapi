"""
Пространство разделов swagger api doc
"""

from flask_restplus import Namespace

ns2 = Namespace('MainPage', description='Приветствие апи', path='/')
ns3 = Namespace('FindPoints', description='Поиск новых точек', path='/parse')
ns4 = Namespace('Points', description='Поиск новых точек', path='/points')
ns5 = Namespace('Map', description='Вывод информации на карту', path='/map')
ns6 = Namespace('Users', description='Вывод информации на карту', path='/')
ns7 = Namespace('CeleryMonitor', description='Работа с заданиями', path='/task')

namespaces_tuple = (ns2, ns3, ns4, ns5, ns6, ns7)
