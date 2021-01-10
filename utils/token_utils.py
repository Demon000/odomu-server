from calendar import timegm
from datetime import datetime
from enum import Enum

from utils.errors import JWTAccessTokenNotFresh


class TokenType(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


def verify_fresh_token(decoded_token: dict):
    fresh = decoded_token['fresh']
    if isinstance(fresh, bool):
        if not fresh:
            raise JWTAccessTokenNotFresh('Fresh field is false')
    elif isinstance(fresh, int):
        now = timegm(datetime.utcnow().utctimetuple())
        if fresh < now:
            raise JWTAccessTokenNotFresh('Fresh field is older than current time')
    else:
        raise JWTAccessTokenNotFresh('Fresh field has invalid type')


def get_token_identity(decoded_token: dict):
    if not decoded_token:
        return None

    return decoded_token['identity']
