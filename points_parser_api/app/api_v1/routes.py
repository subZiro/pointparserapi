"""
Роуты api
"""

from app import app, api
from app.api_v1.endpoints import TaskRevokeCrud, TaskStatusCrud, \
    MainPage, \
    UsersCrud, UserCreateCrud, UserProfileCrud, UserUpdateCrud, UserTokenCrud, \
    MapBasePointsCrud, MapTempPointsCrud, \
    BasePointsCrud, \
    ParsePointsAdmCrud, RefreshPointsAdmCrud, AddPointAdmCrud, RunNormalizeAdmCrud

from app.api_v1.namespaces import *

[api.add_namespace(x) for x in namespaces_tuple]

routes = (
    (MainPage, '/home/', ['GET'], ns2),

    (AddPointAdmCrud, '/add/', ['POST'], ns3),
    (ParsePointsAdmCrud, '/points/', ['POST'], ns3),
    (RefreshPointsAdmCrud, '/refresh/', ['GET'], ns3),
    (RunNormalizeAdmCrud, '/run_normalize/', ['GET'], ns3),

    (BasePointsCrud, '/base/', ['POST'], ns4),

    (MapTempPointsCrud, '/temp_points/', ['POST'], ns5),
    (MapTempPointsCrud, '/temp_point/<int:idx>/', ['GET'], ns5),
    (MapBasePointsCrud, '/base_points/', ['POST'], ns5),
    (MapBasePointsCrud, '/base_point/<int:idx>/', ['GET'], ns5),

    (UserTokenCrud, '/user/token/<int:idx>/', ['GET'], ns6),
    (UserProfileCrud, '/user/profile/', ['GET'], ns6),
    (UserCreateCrud, '/user/create/', ['POST'], ns6),
    (UserUpdateCrud, '/user/update/', ['POST'], ns6),
    (UsersCrud, '/users/', ['POST'], ns6),

    (TaskStatusCrud, '/status/<task_id>/', ['GET'], ns7),
    (TaskRevokeCrud, '/revoke/<task_id>/', ['GET'], ns7),

)

for resource, url, methods, namespace in routes:
    namespace = api if not namespace else namespace
    if methods:
        namespace.add_resource(resource, url, methods=methods)
    else:
        namespace.add_resource(resource, url)


@app.after_request
def add_header(response):
    response.headers['WWW-Authenticate'] = ''
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Credentials', True)
    return response
