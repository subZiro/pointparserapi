# PointParserApi

api проекта PointParser v 1.01

### краткая инструкция по запуску:


##### Развертывание проекта с docker-compose

```
+ перейти в директорию, содержащую файл docker-compose-dev.yml
Выполнить следующие команды:
'docker-compose -f docker-compose-dev.yml rm -sf'
'perl -pi -e 's/docker-compose-stage/docker-compose-dev/g;' ./sh/sleeppostgres.sh'
'docker-compose -f docker-compose-dev.yml build --parallel'
'docker-compose -f docker-compose-dev.yml up -d'

+ проект доступен в по адресу http://localhost:5010/

Запуск тестов:
'docker exec --tty apipointparserdev python3 -m pytest --junitxml=ci_report_test.xml'
```

##### Развертывание проекта без docker-compose

```
+ перейти в директорию, содержащую файл requirements.txt
+ создать виртуальное окружение:
  + python3 -m venv venv
+ активировать виртуальное окружение:
  + source venv/bin/activate
+ pip3 install -r requirements.txt
+ добавить переменные окружения 
  + export FLASK_ENV=development
  + export FLASK_APP="$(pwd)/main.py"
+ выполнить инструкцию развертывания БД

+ flask run -p 5010
проект доступен в по адресу http://localhost:5010/
```


##### Создание базы данных, и заполнение тестовыми данными

```
+ выполнить следующие команды для настройки бд, находясь в директории, содержащей README.md:
  + sudo -u postgres psql -f ./init_database.sql

+ перейти в директорию, сожержащую main.py
  + flask db upgrade
```

##### Проведение тестирования

```
Запуск тестов:
'python3 -m pytest'
```


##### Скриншот api
![Скриншот к проекту](https://github.com/subZiro/pointparserapi/blob/master/points_parser_api/screenshot.png)

----
