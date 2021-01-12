from flask import Blueprint, jsonify, request, Flask, Response, send_file

from api.helpers import retrieve_logged_in_user, retrieve_area, AreaRetrievalType, TokenLocation
from api.pagination import get_paginated_items_from_qs
from models.Area import area_categories_map
from services.AreaService import AreaService

api = Blueprint('api_areas', __name__)


@api.route('/categories')
def areas_get_categories():
    return jsonify(area_categories_map.to_dict())


@api.route('')
@retrieve_logged_in_user()
def areas_get(area_service: AreaService):
    user = request.user

    areas = area_service.find_by(owner=user).order_by('-id')

    return jsonify(get_paginated_items_from_qs(areas))


@api.route('/all')
@retrieve_logged_in_user()
def areas_get_all(area_service: AreaService):
    user = request.user

    areas = area_service.find_by(owner=user).order_by('-id')
    response = [a.to_dict() for a in areas]

    return jsonify(response)


@api.route('', methods=['POST'])
@retrieve_logged_in_user()
def areas_post(area_service: AreaService):
    user = request.user
    name = request.json.get('name')
    category = request.json.get('category')
    location = request.json.get('location')
    location_point = request.json.get('location_point')
    image = request.json.get('image')

    area = area_service.add(user, name, category, location, location_point, image)

    return jsonify(area.to_dict())


@api.route('/<string:area_id>')
@retrieve_logged_in_user()
@retrieve_area(AreaRetrievalType.ID_AND_OWNER)
def areas_get_area():
    area = request.area
    return jsonify(area.to_dict())


@api.route('/<string:area_id>', methods=['PATCH'])
@retrieve_logged_in_user()
@retrieve_area(AreaRetrievalType.ID_AND_OWNER)
def areas_patch_area(area_service: AreaService):
    name = request.json.get('name')
    category = request.json.get('category')
    location = request.json.get('location')
    location_point = request.json.get('location_point')
    image = request.json.get('image')
    updated_at_timestamp = request.json.get('updated_at_timestamp')

    area = request.area

    area_service.update(area, name, category, location, location_point, image, updated_at_timestamp)

    return jsonify(area.to_dict())


@api.route('/<string:area_id>', methods=['DELETE'])
@retrieve_logged_in_user()
@retrieve_area(AreaRetrievalType.ID_AND_OWNER)
def areas_delete_area(area_service: AreaService):
    area = request.area

    area_service.delete(area)

    return Response()


def register_blueprint(app: Flask, prefix: str):
    app.register_blueprint(api, url_prefix=prefix)
