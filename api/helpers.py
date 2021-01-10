import traceback
from enum import Enum
from functools import wraps
from typing import Union

from flask import request, Response
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask_jwt_extended.utils import verify_token_type

from config import ACCESS_TOKEN_HEADER_NAMES, REFRESH_TOKEN_HEADER_NAMES, ACCESS_TOKEN_QUERY_STRING_NAMES, \
    REFRESH_TOKEN_QUERY_STRING_NAMES
from services.AreaService import AreaService
from services.UserService import UserService
from utils.dependencies import services_injector
from utils.errors import UserNotLoggedIn, UserLoggedInInvalid, AreaDoesNotExist, JWTHeaderMissing
from utils.token_utils import verify_fresh_token, TokenType, get_token_identity


def _create_fresh_access_token(username: str):
    return create_access_token(identity=username, fresh=True)


def _create_refresh_token(username: str):
    return create_refresh_token(identity=username)


def set_access_token(response: Response, access_token):
    response.headers[ACCESS_TOKEN_HEADER_NAMES[0]] = access_token


def set_refresh_token(response: Response, refresh_token):
    response.headers[REFRESH_TOKEN_HEADER_NAMES[0]] = refresh_token


def set_new_tokens(response: Response, username: str):
    access_token = _create_fresh_access_token(username)
    set_access_token(response, access_token)
    refresh_token = _create_refresh_token(username)
    set_refresh_token(response, refresh_token)
    return access_token, refresh_token


class TokenLocation(Enum):
    HEADERS = 'headers'
    QUERY_STRING = 'query-string'


def _get_header_names(request_type: TokenType):
    if request_type == TokenType.ACCESS:
        return ACCESS_TOKEN_HEADER_NAMES
    elif request_type == TokenType.REFRESH:
        return REFRESH_TOKEN_HEADER_NAMES

    return None


def _get_header_token(name: str):
    return request.headers.get(name)


def _get_query_param_names(request_type: TokenType):
    if request_type == TokenType.ACCESS:
        return ACCESS_TOKEN_QUERY_STRING_NAMES
    elif request_type == TokenType.REFRESH:
        return REFRESH_TOKEN_QUERY_STRING_NAMES

    return None


def _get_query_param_token(name: str):
    return request.args.get(name)


def _get_encoded_token(request_type: TokenType, get_names_fn, get_token_fn):
    names = get_names_fn(request_type)

    token = None
    for name in names:
        token = get_token_fn(name)
        if token:
            break

    if not token:
        raise JWTHeaderMissing('JWT {} header  missing'.format(request_type))

    return token


def _decode_token(request_type: TokenType, token_location: TokenLocation) -> Union[dict, None]:
    encoded_token = None

    if token_location == TokenLocation.HEADERS:
        encoded_token = _get_encoded_token(request_type, _get_header_names, _get_header_token)
    elif token_location == TokenLocation.QUERY_STRING:
        encoded_token = _get_encoded_token(request_type, _get_query_param_names, _get_query_param_token)

    decoded_token = decode_token(encoded_token)
    verify_token_type(decoded_token, expected_type=request_type.value)
    return decoded_token


def _decode_refresh_token(token_location: TokenLocation):
    decoded_token = _decode_token(TokenType.REFRESH, token_location)
    request.jwt_data = decoded_token


def _decode_fresh_access_token(token_location: TokenLocation):
    decoded_token = _decode_token(TokenType.ACCESS, token_location)
    request.jwt_data = decoded_token
    verify_fresh_token(request.jwt_data)


def _verify_access_token(optional: bool, token_location: TokenLocation) -> Union[str, None]:
    try:
        _decode_refresh_token(token_location)
        username = get_token_identity(request.jwt_data)
    except Exception as e:
        if optional:
            return None
        else:
            raise UserNotLoggedIn(original_message=str(e))

    try:
        _decode_fresh_access_token(token_location)
        return None
    except Exception:
        pass

    return _create_fresh_access_token(username)


def retrieve_logged_in_user(optional: bool = False, token_location: TokenLocation = TokenLocation.HEADERS):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            request.user = None

            access_token = _verify_access_token(optional, token_location)

            username = get_token_identity(request.jwt_data)
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
                area = area_service.find_one_by(owner=user, id=area_id)
            else:
                area = None

            if area is None:
                raise AreaDoesNotExist()

            request.area = area

            return fn(*args, **kwargs)

        return wrapper

    return decorator
