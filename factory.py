from flask import Flask
from flask.ext.session import Session


def create_app(config_override=None):
    application = Flask(__name__)

    import config
    application.config.from_object(config)
    application.config.from_object(config_override)

    Session(application)

    from blueprints.api import api
    api.init_app(application)

    import blueprints
    for blueprint in blueprints.blueprints:
        application.register_blueprint(blueprint)

    return application