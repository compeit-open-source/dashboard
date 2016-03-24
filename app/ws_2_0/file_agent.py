
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

import logging

from flask.ext.socketio import emit

from ..models import FileStorage

logger = logging.getLogger(__name__)


def server_message(message):
    if 'get' in message:
        f = None
        if 'id' in message['get']:
            f = FileStorage.query.filter_by(id=message['get']['id']).first()
        else:
            f = FileStorage.query.filter_by(type=message['get']['type'], externalId=message['get']['externalId']).first()

        if f:
            emit('server_message', {'type': 'file', 'url': f.url})

    emit('server_message', {'type': 'file', 'error': 'command not found'})
