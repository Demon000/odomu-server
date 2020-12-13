from flask import Blueprint, jsonify, request, Flask, Response

from api.helpers import retrieve_logged_in_user, unset_tokens, set_new_tokens
from services.UserService import UserService
from utils.errors import UserLoginFailed

api = Blueprint('api_v1_user', __name__)


@api.route('')
@retrieve_logged_in_user()
def user_get():
    user = request.user
    return jsonify(user.to_dict())


@api.route('/login', methods=['POST'])
def login_post(service: UserService):
    username = request.json.get('username')
    password = request.json.get('password')

    user = service.find_one_by(username=username)
    if user is None:
        raise UserLoginFailed()

    service.verify_password(user, password)

    response = jsonify(user.to_dict())
    set_new_tokens(response, username)

    return response


@api.route('/logout', methods=['POST'])
def logout_post():
    response = Response()
    unset_tokens(response)
    return response


@api.route('/register', methods=['POST'])
def register_post(service: UserService):
    username = request.json.get('username')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')

    user = service.add(username, password, first_name, last_name)
    return jsonify(user.to_dict())


def register_blueprint(app: Flask, prefix: str):
    app.register_blueprint(api, url_prefix=prefix)
