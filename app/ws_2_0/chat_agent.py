
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
from datetime import datetime

from flask.ext.login import current_user

from .. import db

from ..models import User, Event, EventTypes

logger = logging.getLogger(__name__)


def user_joined():
    pass


def user_left():
    pass


def room_message(message):
    e = Event(roomId=current_user.activeRoomId, type=EventTypes.ROOM_CHAT, userId=current_user.id, name=current_user.name, datetime=datetime.utcnow(), text=message['data'])
    db.session.add(e)
    db.session.commit()


def user_message(message):
    e = Event(roomId=current_user.activeRoomId, type=EventTypes.USER_CHAT, userId=current_user.id,  toUser=message['to'], name=current_user.name, datetime=datetime.utcnow(), text=message['data'])
    db.session.add(e)
    db.session.commit()
