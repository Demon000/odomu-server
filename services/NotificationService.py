import json
from enum import Enum
from typing import List

from flask import request
from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import verify_token_type
from flask_socketio import SocketIO, emit
from mongoengine import DoesNotExist
from pyee import EventEmitter

from models.Area import Area
from models.User import User
from utils.errors import JWTHeaderMissing, UserNotLoggedIn
from utils.token_utils import TokenType, verify_fresh_token, get_token_identity


def _find_user_by_username(username: str):
    try:
        return User.objects.get(username=username)
    except DoesNotExist:
        return None


def _verify_access_token(encoded_token: str):
    try:
        decoded_token = decode_token(encoded_token)
        verify_token_type(decoded_token, expected_type=TokenType.ACCESS.value)
        verify_fresh_token(decoded_token)
    except Exception as e:
        raise UserNotLoggedIn(original_message=str(e))

    return decoded_token


class NotificationServiceEvents(Enum):
    AUTHENTICATE_TRY_LINK = 'authenticate-try-link'


class SocketEvents(Enum):
    AREA_ADDED = 'area-added'
    AREA_UPDATED = 'area-updated'
    AREA_DELETED = 'area-deleted'
    AUTHENTICATE_ERROR = 'authenticate-error'
    AUTHENTICATE = 'authenticate'
    AUTHENTICATED = 'authenticated'


class NotificationService:
    def __init__(self, socket_server: SocketIO, debug: bool = False):
        self.socket_server = socket_server
        self.debug = debug
        self.emitter = EventEmitter()
        self.attach_listeners()
        self.sid_to_users_map: dict[str, User] = {}
        self.username_to_sid_map: dict[str, list] = {}

    def emit_to_sid(self, sid: str, name: str, *args):
        emit(name, *args, room=sid, namespace='/')

    def link_user_sid(self, sid: str, user: User):
        self.sid_to_users_map[sid] = user
        self.username_to_sid_map.setdefault(user.username, []).append(sid)

    def unlink_user_sid(self, sid: str, user: User):
        del self.sid_to_users_map[sid]
        self.username_to_sid_map[user.username].remove(sid)

    def get_linked_user(self, sid: str):
        return self.sid_to_users_map.get(sid)

    def get_linked_sids(self, user: User) -> List[str]:
        return self.username_to_sid_map.get(user.username)

    def notify_area_change(self, name: str, area: Area):
        sids = self.get_linked_sids(area.owner)
        if not sids:
            return

        d = area.to_dict()
        for sid in sids:
            self.emit_to_sid(sid, name, d)

    def notify_area_add(self, area: Area):
        self.notify_area_change(SocketEvents.AREA_ADDED.value, area)

    def notify_area_update(self, area: Area):
        self.notify_area_change(SocketEvents.AREA_UPDATED.value, area)

    def notify_area_delete(self, area: Area):
        self.notify_area_change(SocketEvents.AREA_DELETED.value, area)

    def authenticate_link_notify(self, sid: str, user: User):
        self.link_user_sid(sid, user)
        if self.debug:
            print('Client with username {} authenticated'.format(user.username))
        self.emit_to_sid(sid, SocketEvents.AUTHENTICATED.value, user.to_dict())

    def notify_authenticate_error(self, sid: str):
        self.emit_to_sid(sid, SocketEvents.AUTHENTICATE_ERROR.value)
        if self.debug:
            print('Client with sid {} authenticate error'.format(sid))

    def attach_listeners(self):
        @self.socket_server.event
        def connect():
            if self.debug:
                print('Client with id {} connected'.format(request.sid))

        @self.socket_server.on(SocketEvents.AUTHENTICATE.value)
        def on_authenticate(encoded_token):
            if not encoded_token:
                return emit(SocketEvents.AUTHENTICATE_ERROR.value, JWTHeaderMissing().to_dict())

            try:
                decoded_token = _verify_access_token(encoded_token)
            except UserNotLoggedIn as e:
                return emit(SocketEvents.AUTHENTICATE_ERROR.value, e.to_dict())

            username = get_token_identity(decoded_token)

            if self.debug:
                print('Client with id {} and username {} trying to authenticate'.format(request.sid, username))

            self.emitter.emit(NotificationServiceEvents.AUTHENTICATE_TRY_LINK, request.sid, username)

        @self.socket_server.event
        def disconnect():
            user = self.get_linked_user(request.sid)
            if not user:
                return

            self.unlink_user_sid(request.sid, user)

            if self.debug:
                print('Client with username {} disconnected'.format(user.username))
