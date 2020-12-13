class HttpError(Exception):
    def __init__(self, message, code, status):
        super().__init__(message)

        self.code = code
        self.status = status
        self.message = message

    def to_dict(self):
        return {
            'code': self.code,
            'message': self.message,
            'error': True,
        }


def make_http_error(name, code, status, default_message):
    def __init__(self, message=default_message):
        HttpError.__init__(self, message, code, status)

    return type(name, (HttpError,), {
        '__init__': __init__,
    })


UserAlreadyExists = make_http_error('UserAlreadyExists',
                                    'user-already-exists', 403,
                                    'User already exists')
UserDoesNotExist = make_http_error('UserDoesNotExist',
                                   'user-not-exist', 404,
                                   'User does not exist')
UserUsernameInvalid = make_http_error('UserUsernameInvalid',
                                      'user-username-invalid', 400,
                                      'User username is invalid')
UserPasswordInvalid = make_http_error('UserPasswordInvalid',
                                      'user-password-invalid', 400,
                                      'User password is invalid')
UserFirstNameInvalid = make_http_error('UserFirstNameInvalid',
                                       'user-first-name-invalid', 400,
                                       'User first name is invalid')
UserLastNameInvalid = make_http_error('UserLastNameInvalid',
                                      'user-last-name-invalid', 400,
                                      'User last name is invalid')
UserLoginFailed = make_http_error('UserLoginFailed',
                                  'user-login-failed', 401,
                                  'User login failed')
UserNotLoggedIn = make_http_error('UserNotLoggedIn',
                                  'user-not-logged-in', 401,
                                  'User not logged in')
UserLoggedInInvalid = make_http_error('UserLoggedInInvalid',
                                      'user-logged-in-invalid', 401,
                                      'User logged in is invalid')
UserTokenExpired = make_http_error('UserTokenExpired',
                                   'user-token-expired', 401,
                                   'User token expired')
UserTokenInvalid = make_http_error('UserTokenInvalid',
                                   'user-token-invalid', 422,
                                   'User token is invalid')
