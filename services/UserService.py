from typing import Union

from mongoengine import DoesNotExist, NotUniqueError

from models.User import User

from utils.errors import UserAlreadyExists, UserLoginFailed
from validators.UserValidator import UserValidator


class UserService:
    def __init__(self, validator: UserValidator):
        self.validator = validator

    def add(self, username: str, password: str, first_name: str, last_name: str) -> User:
        self.validator.validate_parameters(username, password, first_name, last_name)

        user = User(username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)

        try:
            user.save()
        except NotUniqueError:
            raise UserAlreadyExists()

        return user

    def verify_password(self, user: User, password: str):
        if not user.is_correct_password(password):
            raise UserLoginFailed()

    def find_one_by(self, *args, **kwargs) -> Union[User, None]:
        try:
            return User.objects.get(*args, **kwargs)
        except DoesNotExist:
            return None
