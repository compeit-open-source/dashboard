
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

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'HEMLIGT'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    DASHBOARD_MAIL_SUBJECT_PREFIX = 'COMPEIT Dashboard -'
    DASHBOARD_MAIL_SENDER = 'dashboard@prototype.compeit.eu'
    MAIL_SERVER = 'prototype.compeit.eu'
    MAIL_CONFIRM = True
    DEFAULT_FILE_STORAGE = 'filesystem'
    UPLOADS_DEFAULT_DEST = 'uploads'
    STATISTICS = True
    # UPLOADED_AVATARS_DEST = 'app/uploads'
    IA_ENABLED = True
    ONLY_IMMERSIVE_SPACE = True
    IA_URL = 'http://prototype.compeit.eu:9004/'  # Information Agent
    CA_URL = 'ws://prototype.compeit.eu:9002'  # Connection Agent
    EP_URL = 'http://prototype.compeit.eu:9006'  # Etherpad lite
    ER_URL = 'http://prototype.compeit.eu:9008'  # easyRTC
    MDS_URL = 'http://prototype.compeit.eu:8010'
    # SERVER_NAME = 'https://prototype.compeit.eu:9443/'
    MD_URL = 'http://prototype.compeit.eu:8012/js/master-proxy.js' # Multi-device server
    VIDEO_APP_KEY = 'To be defined'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfigLocal(Config):
    DEBUG = True
    ONLY_IMMERSIVE_SPACE = False
    MAIL_CONFIRM = False
    IA_ENABLED = True
    #IA_URL = 'http://127.0.0.1:9091/'  # Information Agent
    CA_URL = 'ws://prototype.compeit.eu:9002'  # Connection Agent
    EP_URL = 'http://prototype.compeit.eu:9006'  # Etherpad lite
    ER_URL = 'http://prototype.compeit.eu:9008'  # easyRTC
    MDS_URL = 'http://prototype.compeit.eu:8010'

    #MD_URL = 'http://pmc.research.ltu.se:8012/js/master-proxy.js' # Multi-device server
    VIDEO_APP_KEY = 'To be defined'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev-local.sqlite')


class DevelopmentConfigSprint(Config):
    DEBUG = True
    MAIL_CONFIRM = False
    IA_ENABLED = True
    ONLY_IMMERSIVE_SPACE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev-sprint.sqlite')


class DevelopmentConfigStable(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev-stable.sqlite')


class DevelopmentConfigPilot(Config):
    DEBUG = True
    ONLY_IMMERSIVE_SPACE = True
    MAIL_CONFIRM = True
    IA_ENABLED = False

    ER_URL = 'http://pilot-er.compeit.eu'  # easyRTC
    #MD_URL = 'http://pmc.research.ltu.se:8012/js/master-proxy.js'  # Multi-device server
    VIDEO_APP_KEY = 'To be defined'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-pilot.sqlite')


class DevelopmentConfigPilotWorkers(Config):
    DEBUG = True
    ONLY_IMMERSIVE_SPACE = True
    MAIL_CONFIRM = True
    IA_ENABLED = False

    ER_URL = 'http://workers-er.compeit.eu'  # easyRTC
    #MD_URL = 'http://pmc.research.ltu.se:8012/js/master-proxy.js'  # Multi-device server
    VIDEO_APP_KEY = 'To be defined'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-workers.sqlite')


class DevelopmentConfigPilotStudents(Config):
    DEBUG = True
    ONLY_IMMERSIVE_SPACE = True
    MAIL_CONFIRM = True
    IA_ENABLED = False

    ER_URL = 'http://students-er.compeit.eu'  # easyRTC
    #MD_URL = 'http://pmc.research.ltu.se:8012/js/master-proxy.js'  # Multi-device server
    VIDEO_APP_KEY = 'To be defined'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-students.sqlite')


class DevelopmentConfigPilotFamilies(Config):
    DEBUG = True
    ONLY_IMMERSIVE_SPACE = True
    MAIL_CONFIRM = True
    IA_ENABLED = False

    ER_URL = 'http://families-er.compeit.eu'  # easyRTC
    #MD_URL = 'http://pmc.research.ltu.se:8012/js/master-proxy.js'  # Multi-device server
    VIDEO_APP_KEY = 'To be defined'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-families.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development_local': DevelopmentConfigLocal,
    'development_sprint': DevelopmentConfigSprint,
    'development_stable': DevelopmentConfigStable,
    'pilot': DevelopmentConfigPilot,
    'pilot_workers': DevelopmentConfigPilotWorkers,
    'pilot_students': DevelopmentConfigPilotStudents,
    'pilot_families': DevelopmentConfigPilotFamilies,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfigLocal
}
