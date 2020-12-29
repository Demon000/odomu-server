from models.Area import area_categories_map


class APIError(Exception):
    def __init__(self, code, status, message, *args, error_type='api-error', original_message=None, **kwargs):
        super().__init__(message)

        self.code = code
        self.status = status
        self.message = message
        self.original_message = original_message
        self.error_type = error_type

    def to_dict(self):
        return {
            'code': self.code,
            'message': self.message,
            'original_message': self.original_message,
            'error': True,
            'type': self.error_type,
        }


class ValidationError(APIError):
    def __init__(self, code, status, message, field_name, valid_values=None, *args, **kwargs):
        super().__init__(code, status, message, *args, error_type='validation-error', **kwargs)

        self.field_name = field_name
        self.valid_values = valid_values

    def to_dict(self):
        d = super().to_dict()
        d.update({
            'field_name': self.field_name,
        })

        if self.valid_values:
            d['valid_values'] = self.valid_values

        return d


class MultiError(APIError):
    def __init__(self, code, status, message, errors=None, *args, **kwargs):
        super().__init__(code, status, message, *args, error_type='multi-error', **kwargs)

        if errors is None:
            errors = []

        self.errors = errors

    def add_error(self, error: Exception):
        if isinstance(error, MultiError) and error.code == self.code:
            self.errors.extend(error.errors)
        else:
            self.errors.append(error)

    def is_empty(self):
        return not len(self.errors)

    def to_dict(self):
        d = super().to_dict()
        d.update({
            'errors': [e.to_dict() for e in self.errors]
        })
        return d


def make_error(base_class, name, code, status, default_message, **default_kwargs):
    def __init__(self, message=default_message, **kwargs):
        merged_kwargs = {}
        merged_kwargs.update(default_kwargs)
        merged_kwargs.update(kwargs)
        base_class.__init__(self, code, status, message, **merged_kwargs)

    return type(name, (base_class,), {
        '__init__': __init__,
    })


def make_api_error(name, code, status, message, **kwargs):
    return make_error(APIError, name, code, status, message, **kwargs)


def make_validation_error(name, code, status, message, **kwargs):
    return make_error(ValidationError, name, code, status, message, **kwargs)


def make_multi_error(name, code, status, message, **kwargs):
    return make_error(MultiError, name, code, status, message, **kwargs)


PaginationLimitInvalid = make_api_error('PaginationLimitInvalid',
                                        'pagination-limit-invalid', 400,
                                        'Pagination limit invalid')
PaginationPageInvalid = make_api_error('PaginationPageInvalid',
                                       'pagination-page-invalid', 400,
                                       'Pagination page invalid')

UserAlreadyExists = make_api_error('UserAlreadyExists',
                                   'user-already-exists', 403,
                                   'User already exists')
UserDoesNotExist = make_api_error('UserDoesNotExist',
                                  'user-not-exist', 404,
                                  'User does not exist')
UserLoginFailed = make_api_error('UserLoginFailed',
                                 'user-login-failed', 401,
                                 'User login failed')
UserNotLoggedIn = make_api_error('UserNotLoggedIn',
                                 'user-not-logged-in', 401,
                                 'User not logged in')
UserLoggedInInvalid = make_api_error('UserLoggedInInvalid',
                                     'user-logged-in-invalid', 401,
                                     'User logged in is invalid')
UserTokenExpired = make_api_error('UserTokenExpired',
                                  'user-token-expired', 401,
                                  'User token expired')
UserTokenInvalid = make_api_error('UserTokenInvalid',
                                  'user-token-invalid', 422,
                                  'User token is invalid')

UserAddFailed = make_multi_error('UserAddFailed',
                                 'user-add-failed', 400,
                                 'User add failed')

UserUsernameInvalid = make_validation_error('UserUsernameInvalid',
                                            'user-username-invalid', 400,
                                            'Is invalid',
                                            field_name='username')
UserPasswordInvalid = make_validation_error('UserPasswordInvalid',
                                            'user-password-invalid', 400,
                                            'Is invalid',
                                            field_name='password')
UserFirstNameInvalid = make_validation_error('UserFirstNameInvalid',
                                             'user-first-name-invalid', 400,
                                             'Is invalid',
                                             field_name='first_name')
UserLastNameInvalid = make_validation_error('UserLastNameInvalid',
                                            'user-last-name-invalid', 400,
                                            'Is invalid',
                                            field_name='last_name')

AreaDoesNotExist = make_api_error('AreaDoesNotExist',
                                  'area-not-exist', 404,
                                  'Area does not exist')

AreaAddFailed = make_multi_error('AreaAddFailed',
                                 'area-add-failed', 400,
                                 'Area add failed')
AreaUpdateFailed = make_multi_error('AreaUpdateFailed',
                                    'area-update-failed', 400,
                                    'Area update failed')

AreaOwnerInvalid = make_validation_error('AreaOwnerInvalid',
                                         'area-owner-invalid', 400,
                                         'Is invalid',
                                         field_name='owner')
AreaNameInvalid = make_validation_error('AreaNameInvalid',
                                        'area-name-invalid', 400,
                                        'Is invalid',
                                        field_name='name')
AreaCategoryInvalid = make_validation_error('AreaCategoryInvalid',
                                            'area-category-invalid', 400,
                                            'Is invalid',
                                            field_name='category',
                                            valid_values=area_categories_map.values())
AreaLocationInvalid = make_validation_error('AreaLocationInvalid',
                                            'area-location-invalid', 400,
                                            'Is invalid',
                                            field_name='location')
