from flask import Flask, Blueprint, request, jsonify

from api.helpers import retrieve_logged_in_user
from geopy.geocoders import Nominatim

from config import GEOCODE_USER_AGENT
from utils.errors import GeocodeLatitudeInvalid, GeocodeLongitudeInvalid, GeocodeAddressInvalid, GeocodeForwardFailed, \
    GeocodeReverseFailed

api = Blueprint('api_geocode', __name__)
geolocator = Nominatim(user_agent=GEOCODE_USER_AGENT)


@api.route('forward')
@retrieve_logged_in_user()
def forward_get():
    address = request.args.get('address')

    if not address:
        raise GeocodeAddressInvalid()

    results = geolocator.geocode(address)
    if not results:
        raise GeocodeForwardFailed()

    return jsonify({
        'address': results.raw['display_name'],
        'latitude': results.raw['lat'],
        'longitude': results.raw['lon'],
    })


@api.route('reverse')
@retrieve_logged_in_user()
def reverse_get():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude:
        raise GeocodeLatitudeInvalid()

    if not longitude:
        raise GeocodeLongitudeInvalid()

    results = geolocator.reverse((latitude, longitude))
    if not results:
        raise GeocodeReverseFailed()

    return jsonify({
        'address': results.raw['display_name'],
    })


def register_blueprint(app: Flask, prefix: str):
    app.register_blueprint(api, url_prefix=prefix)
