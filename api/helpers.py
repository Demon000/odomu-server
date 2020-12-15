from enum import Enum
from functools import wraps

from flask import request, Response
from flask_jwt_extended import get_jwt_identity, verify_jwt_refresh_token_in_request, \
    create_access_token, set_access_cookies, create_refresh_token, set_refresh_cookies, verify_fresh_jwt_in_request, \
    unset_access_cookies, unset_refresh_cookies
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, FreshTokenRequired
from jwt import ExpiredSignatureError

from services.AreaService import AreaService
from services.UserService import UserService
from utils.dependencies import services_injector
from utils.errors import UserNotLoggedIn, UserLoggedInInvalid, AreaDoesNotExist


def _create_fresh_access_token(username: str):
    return create_access_token(identity=username, fresh=True)


def _create_refresh_token(username: str):
    return create_refresh_token(identity=username)


def set_access_token(response: Response, access_token):
    set_access_cookies(response, access_token)


def set_refresh_token(response: Response, refresh_token):
    set_refresh_cookies(response, refresh_token)


def set_new_tokens(response: Response, username: str):
    access_token = _create_fresh_access_token(username)
    set_access_token(response, access_token)
    refresh_token = _create_refresh_token(username)
    set_refresh_token(response, refresh_token)
    return access_token, refresh_token


def unset_tokens(response: Response):
    unset_access_cookies(response)
    unset_refresh_cookies(response)


def verify_access_token(optional=False):
    try:
        verify_jwt_refresh_token_in_request()
        username = get_jwt_identity()
    except (NoAuthorizationError, InvalidHeaderError):
        if optional:
            return
        else:
            raise UserNotLoggedIn()

    try:
        verify_fresh_jwt_in_request()
        return None
    except ExpiredSignatureError:
        pass

    return _create_fresh_access_token(username)


def retrieve_logged_in_user(optional=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            request.user = None

            access_token = verify_access_token(optional)

            username = get_jwt_identity()
            if not username:
                if optional:
                    return
                else:
                    raise UserNotLoggedIn()

            user_service = services_injector.get(UserService)
            user = user_service.find_one_by(username=username)
            if not user:
                raise UserLoggedInInvalid()

            request.user = user

            response = fn(*args, **kwargs)

            if access_token is not None:
                set_access_token(response, access_token)

            return response

        return wrapper

    return decorator


class AreaRetrievalType(Enum):
    ID_AND_OWNER = 2


def retrieve_area(retrieval_type: AreaRetrievalType):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = request.user

            request.event = None

            area_id = kwargs.pop('area_id')
            if not area_id:
                raise AreaDoesNotExist()

            area_service = services_injector.get(AreaService)
            if retrieval_type == AreaRetrievalType.ID_AND_OWNER:
                area = area_service.find_by(owner=user, id=area_id)
            else:
                area = None

            if area is None:
                raise AreaDoesNotExist()

            request.area = area

            return fn(*args, **kwargs)

        return wrapper

    return decorator
