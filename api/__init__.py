from flask import Blueprint, jsonify, Flask

from api.user import register_blueprint as register_user_api_blueprint
from api.areas import register_blueprint as register_areas_api_blueprint

api = Blueprint('api', __name__)


@api.route('/ping')
def about():
    return jsonify({
        'description': 'API endpoint',
    })


def register_blueprint(app: Flask, url_prefix: str):
    app.register_blueprint(api, url_prefix=url_prefix)
    register_user_api_blueprint(app, '{}/user'.format(url_prefix))
    register_areas_api_blueprint(app, '{}/areas'.format(url_prefix))
