from typing import Union

from mongoengine import DoesNotExist, NotUniqueError

from models.User import User

from utils.errors import UserAlreadyExists, UserLoginFailed, UserAddFailed, UserUsernameInvalid, UserPasswordInvalid, \
    UserFirstNameInvalid, UserLastNameInvalid
from validators.UserValidator import UserValidator


class UserService:
    def __init__(self, validator: UserValidator):
        self.__validator = validator

    def add(self, username: str, password: str, first_name: str, last_name: str) -> User:
        me = UserAddFailed()

        try:
            self.__validator.validate_username(username)
        except UserUsernameInvalid as e:
            me.add_error(e)

        try:
            self.__validator.validate_password(password)
        except UserPasswordInvalid as e:
            me.add_error(e)

        try:
            self.__validator.validate_first_name(first_name)
        except UserFirstNameInvalid as e:
            me.add_error(e)

        try:
            self.__validator.validate_last_name(last_name)
        except UserLastNameInvalid as e:
            me.add_error(e)

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
