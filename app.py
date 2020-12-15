#!/usr/bin/env python3

import traceback

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_injector import FlaskInjector

from api import register_blueprint as register_api_blueprint
from config import JWT_SECRET_KEY, JWT_TOKEN_LOCATION, JWT_COOKIE_CSRF_PROTECT
from database import connect_database_from_config
from utils.dependencies import services_injector
from utils.errors import APIError, UserTokenExpired, UserTokenInvalid

connect_database_from_config()

app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
app.config['JWT_COOKIE_CSRF_PROTECT'] = JWT_COOKIE_CSRF_PROTECT
jwt = JWTManager(app)

register_api_blueprint(app, '/api')

FlaskInjector(app=app, injector=services_injector)


@app.errorhandler(APIError)
def http_errorhandler(e):
    return jsonify(e.to_dict()), e.status


@app.errorhandler(Exception)
def generic_errorhandler(e: Exception):
    try:
        raise e
    except Exception:
        trace = traceback.format_exc()

    trace_lines = trace.split('\n')

    response = {
        'message': str(e),
        'code': 'unknown-error',
        'stack': trace_lines,
    }
    return jsonify(response), 500


@jwt.expired_token_loader
def expired_token_loader(expired_token):
    return http_errorhandler(UserTokenExpired('User {} token expired'.format(expired_token['type'])))


@jwt.invalid_token_loader
@jwt.unauthorized_loader
def invalid_token_loader(reason):
    return http_errorhandler(UserTokenInvalid('User token is invalid: {}'.format(reason)))
