from injector import Injector, singleton

from services.AreaService import AreaService
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


services_injector = Injector([configure_services])
