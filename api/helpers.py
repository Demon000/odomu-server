from enum import Enum
from functools import wraps
from datetime import datetime
from calendar import timegm

from flask import request, Response
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token, decode_token, \
    get_unverified_jwt_headers
from flask_jwt_extended.utils import verify_token_type

from config import ACCESS_TOKEN_HEADER_NAMES, REFRESH_TOKEN_HEADER_NAMES
from services.AreaService import AreaService
from services.UserService import UserService
from utils.dependencies import services_injector
from utils.errors import UserNotLoggedIn, UserLoggedInInvalid, AreaDoesNotExist, JWTHeaderMissing, \
    JWTAccessTokenNotFresh


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


class TokenType(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


def _get_encoded_token(request_type: TokenType):
    if request_type == TokenType.ACCESS:
        header_names = ACCESS_TOKEN_HEADER_NAMES
    elif request_type == TokenType.REFRESH:
        header_names = REFRESH_TOKEN_HEADER_NAMES
    else:
        raise RuntimeError('Invalid request type {}'.format(request_type))

    header = None
    for header_name in header_names:
        header = request.headers.get(header_name)
        if header:
            break

    if not header:
        raise JWTHeaderMissing('JWT {} header  missing'.format(request_type))

    return header


def _decode_token_from_request(request_type: TokenType):
    encoded_token = _get_encoded_token(request_type)
    decoded_token = decode_token(encoded_token)
    jwt_header = get_unverified_jwt_headers(encoded_token)
    verify_token_type(decoded_token, expected_type=request_type.value)

    return decoded_token, jwt_header


def _verify_token_in_request(request_type: TokenType):
    jwt_data, jwt_header = _decode_token_from_request(request_type)
    request.jwt_data = jwt_data
    request.jwt_header = jwt_header


def _verify_refresh_token_in_request():
    _verify_token_in_request(TokenType.REFRESH)


def _verify_fresh_token_in_request():
    _verify_token_in_request(TokenType.ACCESS)

    fresh = request.jwt_data['fresh']
    if isinstance(fresh, bool):
        if not fresh:
            raise JWTAccessTokenNotFresh('Fresh field is false')
    elif isinstance(fresh, int):
        now = timegm(datetime.utcnow().utctimetuple())
        if fresh < now:
            raise JWTAccessTokenNotFresh('Fresh field is older than current time')
    else:
        raise JWTAccessTokenNotFresh('Fresh field has invalid type')


def _get_token_identity():
    return request.jwt_data['identity']


def _verify_access_token(optional=False):
    try:
        _verify_refresh_token_in_request()
        username = _get_token_identity()
    except Exception as e:
        print(e)
        if optional:
            return
        else:
            raise UserNotLoggedIn(original_message=str(e))

    try:
        _verify_fresh_token_in_request()
        return None
    except Exception:
        pass

    return _create_fresh_access_token(username)


def retrieve_logged_in_user(optional=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            request.user = None

            access_token = _verify_access_token(optional)

            username = _get_token_identity()
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
