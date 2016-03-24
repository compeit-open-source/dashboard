
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

from flask.ext.restful import Resource, fields, marshal
from flask.ext.login import current_user

from . import rapi
from .authentication import requires_auth
from .. import db
from ..models import Room, RoomComponent

room_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.Integer(attribute='componentId'),
    'ownerId': fields.Integer
}

roomtypes_fields = {
    'id': fields.Integer,
    'name': fields.String
}


class RoomAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(RoomAPI, self).__init__()

    def get(self, id, api_user):
        room = Room.query.filter_by(id=id, ownerId=api_user.id).first()
        return {'room': map(lambda t: marshal(t, room_fields), room)}

    def put(self, api_user):
        args = self.reqparse.parse_args()
        room = Room(name=args['name'], ownerId=api_user.id)
        db.session.add(room)
        db.session.commit()
        return {'room': marshal(room, room_fields)}, 201


class RoomListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(RoomListAPI, self).__init__()

    def get(self, api_user):
        rooms = []
        for room in Room.query.all():
            if room.get_permissions(current_user):
                rooms += [room]

        return {'rooms': map(lambda t: marshal(t, room_fields), rooms)}


class RoomTypeListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(RoomTypeListAPI, self).__init__()

    def get(self, api_user):
        room_types = RoomComponent.query.all()
        return {'room_types': map(lambda t: marshal(t, roomtypes_fields), room_types)}


rapi.add_resource(RoomAPI, '/room/<int:id>')
rapi.add_resource(RoomListAPI, '/rooms')
rapi.add_resource(RoomTypeListAPI, '/room_types')
