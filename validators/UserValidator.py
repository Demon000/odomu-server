from utils.errors import UserUsernameInvalid, UserPasswordInvalid, UserFirstNameInvalid, UserLastNameInvalid


class UserValidator:
    def validate_username(self, value: str):
        if not value:
            raise UserUsernameInvalid(message='Username cannot be empty')

    def validate_password(self, value: str):
        if not value:
            raise UserPasswordInvalid(message='Password cannot be empty')

    def validate_first_name(self, value: str):
        if not value:
            raise UserFirstNameInvalid(message='First name cannot be empty')

    def validate_last_name(self, value: str):
        if not value:
            raise UserLastNameInvalid(message='Last name cannot be empty')

    def validate_parameters(self, username: str, password: str, first_name: str, last_name: str):
        self.validate_username(username)
        self.validate_password(password)
        self.validate_first_name(first_name)
        self.validate_last_name(last_name)
