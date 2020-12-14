from utils.errors import UserUsernameInvalid, UserPasswordInvalid, UserFirstNameInvalid, UserLastNameInvalid
from validators.Validator import Validator


class UserValidator(Validator):
    def validate_username(self, value: str):
        self.validate_str('User username', UserUsernameInvalid, value)

    def validate_password(self, value: str):
        self.validate_str('User password', UserPasswordInvalid, value)

    def validate_first_name(self, value: str):
        self.validate_str('User first name', UserFirstNameInvalid, value)

    def validate_last_name(self, value: str):
        self.validate_str('User last name', UserFirstNameInvalid, value)
