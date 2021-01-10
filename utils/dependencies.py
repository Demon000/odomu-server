from injector import Injector, singleton
from flask_socketio import SocketIO

from services.AreaService import AreaService, AreaServiceEvents
from services.NotificationService import NotificationService, NotificationServiceEvents
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

    socket_server = SocketIO(cors_allowed_origins='*')
    binder.bind(SocketIO, to=socket_server, scope=singleton)

    notification_service = NotificationService(socket_server)
    binder.bind(NotificationService, to=notification_service, scope=singleton)

    area_service.emitter.on(AreaServiceEvents.AREA_ADDED, notification_service.notify_area_add)
    area_service.emitter.on(AreaServiceEvents.AREA_UPDATED, notification_service.notify_area_update)
    area_service.emitter.on(AreaServiceEvents.AREA_DELETED, notification_service.notify_area_delete)

    def notification_service_on_authentication_try_link(sid: str, username: str):
        user = user_service.find_one_by(username=username)
        if not user:
            notification_service.notify_authenticate_error(sid)
            return

        notification_service.authenticate_link_notify(sid, user)

    notification_service.emitter.on(NotificationServiceEvents.AUTHENTICATE_TRY_LINK,
                                    notification_service_on_authentication_try_link)


services_injector = Injector([configure_services])
