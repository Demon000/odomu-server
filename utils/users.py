from typing import List

from services.UserService import UserService
from utils.dependencies import services_injector
from utils.errors import UserAlreadyExists


def create_default_users_from_config(users: List[dict]):
    user_service = services_injector.get(UserService)

    for user in users:
        try:
            user_service.add(user['username'], user['password'], user['first_name'], user['last_name'])
        except UserAlreadyExists as e:
            print(e)
