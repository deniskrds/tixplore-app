""" API Blueprint Application """

from quart import Blueprint, current_app

api_bp = Blueprint('api_bp', __name__,)


@api_bp.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


# Import resources to ensure view is registered
from .routes import * # NOQA