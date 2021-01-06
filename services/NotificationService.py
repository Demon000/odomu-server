from flask import request
from flask_socketio import SocketIO, emit


class NotificationService:
    def __init__(self, socket_server: SocketIO):
        self.socket_server = socket_server
        self.attach_listeners()
        self.users = {}

    def attach_listeners(self):
        @self.socket_server.event
        def connect():
            print('Client with id {} connected'.format(request.sid))

        @self.socket_server.event
        def disconnect():
            print('Client with id {} disconnected'.format(request.sid))
