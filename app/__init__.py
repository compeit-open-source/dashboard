
# Copyright 2016 The COMPEIT Consortium
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import pydenticon
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.socketio import SocketIO
from flask.ext.mail import Mail
from flask.ext.triangle import Triangle
from flask.ext.uploads import UploadSet, IMAGES, DEFAULTS, AUDIO, configure_uploads, patch_request_class
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
mail = Mail()
socketio = SocketIO()
triangle = Triangle()

avatars = UploadSet('avatars', IMAGES)

# Set-up a list of foreground colours (taken from Sigil).
foreground = ["rgb(45,79,255)",
              "rgb(254,180,44)",
              "rgb(226,121,234)",
              "rgb(30,179,253)",
              "rgb(232,77,65)",
              "rgb(49,203,115)",
              "rgb(141,69,170)"]
# Set-up a background colour (taken from Sigil).
background = "rgb(224,224,224)"
generator = pydenticon.Generator(8, 8, digest=hashlib.sha1, foreground=foreground, background=background)


def print_routes(app):
    for route in app.url_map.iter_rules():
        print route.rule


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    triangle.init_app(app)
    configure_uploads(app, avatars)

    # Limit uploads to 50 megabyte files
    patch_request_class(app, 50 * 1024 * 1024)

    # routes and custom error pages

    with app.app_context():
        from main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from .admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin')

        # from .restful_api import restful_api as restful_api_blueprint
        # app.register_blueprint(restful_api_blueprint)

        from .api_2_0 import api as api_2_0_blueprint
        app.register_blueprint(api_2_0_blueprint, url_prefix='/api/v2.0')

        from .ws_2_0 import ws as ws_2_0_blueprint
        app.register_blueprint(ws_2_0_blueprint)

        # print_routes(app)

    return app
