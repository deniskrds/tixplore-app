"""
Global Flask Application Setting

See `.flaskenv` for default settings.
 """

import os
from app import app


class Config(object):
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    SECRET_KEY = os.getenv('FLASK_SECRET', 'secret-key')
    DATABASE_URI = "postgres://postgres@localhost:5432/tixplore"
    MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
    SALT = os.getenv('SALT', 'salt')


app.config.from_object('app.config.Config')
