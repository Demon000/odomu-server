#!/usr/bin/env python3
from database import connect_database_from_config
from services.AreaService import AreaService
from services.UserService import UserService
from utils.dependencies import services_injector
from utils.errors import UserAddFailed, AreaAddFailed, UserAlreadyExists

connect_database_from_config()

user_service = services_injector.get(UserService)
area_service = services_injector.get(AreaService)

users_data = [
    ['admin', 'test', 'Admin', 'Test'],
    ['ct', 'test', 'Cosmin', 'Tanislav'],
]
users = []

for user_data in users_data:
    try:
        user = user_service.add(user_data[0], user_data[1], user_data[2], user_data[3])
    except (UserAddFailed, UserAlreadyExists) as e:
        user = user_service.find_one_by(username=user_data[0])
        print(e)

    users.append(user)

for user in users:
    try:
        for i in range(10):
            area_service.add(user, '{} My home'.format(i), 0, 'Aleea Putna, Nr. 4, Cluj-Napoca',
                             [30.4, 20.5])
            area_service.add(user, '{} My office'.format(i), 0, 'Bulevardul 21 Decembrie 1989 77, Cluj-Napoca',
                             [35.4, 20.5])
    except AreaAddFailed as e:
        print(e)
