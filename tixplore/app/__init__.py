import os
from datetime import timedelta

from quart import Quart, jsonify
from quart_rate_limiter import RateLimiter, RateLimit
from quart_schema import QuartSchema, RequestSchemaValidationError
from quart_auth import QuartAuth
from tortoise.contrib.quart import register_tortoise
from tortoise import Tortoise

from .api import api_bp

app = Quart(__name__)
from .config import Config  # noqa

QuartSchema(app)


@app.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return {
        "errors": "Request validation error",
    }, 400


QuartAuth(app)

rate_limiter = RateLimiter(default_limits=[RateLimit(10, timedelta(seconds=5))])
rate_limiter.init_app(app)

app.register_blueprint(api_bp)

register_tortoise(
    app,
    db_url=app.config['DATABASE_URI'],
    modules={"models": ["app.models"]},
    generate_schemas=False,
)

app.logger.info('>>> {}'.format(Config.FLASK_ENV))


@app.route('/')
async def index_client():
    return jsonify({'message': 'Hello, World!'})


async def init_tortoise():
    await Tortoise.init(
        db_url=app.config['DATABASE_URI'],
        modules={"models": ["app.models"]},  # Replace with your actual module path
    )
