import logging.config
from os import environ

import redis
from celery import Celery
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .config import config as app_config

APPLICATION_ENV = environ.get('APPLICATION_ENV') or 'development'
celery = Celery(__name__)
redis_client = redis.Redis(
    host=app_config[APPLICATION_ENV].REDIS_HOST,
    port=app_config[APPLICATION_ENV].REDIS_PORT,
    decode_responses=True)


def create_app():
    # loading env vars from .env file
    load_dotenv()
    logging.config.dictConfig(app_config[APPLICATION_ENV].LOGGING)
    app = Flask(app_config[APPLICATION_ENV].APP_NAME)
    app.config.from_object(app_config[APPLICATION_ENV])

    CORS(app, resources={r'/api/*': {'origins': '*'}})

    celery.config_from_object(app.config, force=True)
    # celery is not able to pick result_backend and hence using update
    celery.conf.update(result_backend=app.config['RESULT_BACKEND'])

    from .core.views import core as core_blueprint
    app.register_blueprint(
        core_blueprint,
        url_prefix='/api/v1/core'
    )

    return app
