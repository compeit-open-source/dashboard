#!/usr/bin/env python

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
import logging

from gevent import monkey
monkey.patch_all()

from app import create_app, db, socketio
from app.models import User, Role, Room, RoomComponent, Object, Widget, StatisticEvent
from app.models import create_sample_db, add_event

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# initialize logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# check installation (errors in Flask-uploads)
from os import name
from os.path import isdir, islink

if name == 'posix':
    if not isdir('app/uploads') or not islink('uploads'):
        logger.error("Please verify that app/uploads directory exits and that uploads is a symbolic link to it.")
        exit()
elif name == 'nt':
    if not isdir('app/uploads') or not isdir('uploads'):
        logger.error("Please verify that app/uploads directory exits and that uploads is a symbolic link to it.")
        exit()

    logger.error("Please make sure that uploads is a symbolic link to the app/uploads directory.")

# create application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Room=Room, RoomComponent=RoomComponent, Widget=Widget, Object=Object)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def sample_db():
    create_sample_db()


@manager.command
def server():
    socketio.run(app, host='0.0.0.0', port=16000, policy_server=False)

if __name__ == '__main__':
    manager.run()
