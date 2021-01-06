from injector import Injector, singleton
from flask_socketio import SocketIO

from services.AreaService import AreaService
from services.NotificationService import NotificationService
from services.UserService import UserService
from validators.AreaValidator import AreaValidator
from validators.UserValidator import UserValidator


def configure_services(binder):
    user_validator = UserValidator()
    user_service = UserService(user_validator)
    binder.bind(UserService, to=user_service, scope=singleton)

    area_validator = AreaValidator()
    area_service = AreaService(area_validator)
    binder.bind(AreaService, to=area_service, scope=singleton)

    socket_server = SocketIO(cors_allowed_origins='*', logger=True, engineio_logger=True)
    binder.bind(SocketIO, to=socket_server, scope=singleton)

    notification_service = NotificationService(socket_server)
    binder.bind(NotificationService, to=notification_service, scope=singleton)


services_injector = Injector([configure_services])
