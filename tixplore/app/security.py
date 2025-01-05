""" Security Related things """
from functools import wraps
from quart import request, abort
from quart_auth import current_user, login_required

from app.models import ApiKeys


def api_key_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            abort(401, description="API key is missing")

        # Retrieve the first API key from the database
        key = await ApiKeys.filter(key=api_key).first()

        if not key:
            abort(403, description="Invalid API key")

        return await f(*args, **kwargs)

    return decorated_function
