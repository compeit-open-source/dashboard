
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

from flask import abort
from flask.ext.restful import Resource, reqparse, fields, marshal

from . import rapi
from .authentication import requires_auth
from .. import db
from ..models import Connection, Object

connection_fields = {
    'id': fields.Integer,
    'output': fields.Integer(attribute='outId'),
    'from': fields.Integer(attribute='output.objectId'),
    'out': fields.String(attribute='output.name'),
    'input': fields.Integer(attribute='inId'),
    'to': fields.Integer(attribute='input.objectId'),
    'in': fields.String(attribute='input.name')
}


class ConnectionListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('from', type=str, location='json')
        self.reqparse.add_argument('in', type=str, location='json')
        self.reqparse.add_argument('to', type=str, location='json')
        self.reqparse.add_argument('out', type=str, location='json')
        super(ConnectionListAPI, self).__init__()

    def get(self, api_user):
        connections = Connection.query.all()
        return {'connections': map(lambda t: marshal(t, connection_fields), connections)}

    def post(self, api_user):
        args = self.reqparse.parse_args()
        c = Object.query.filter_by(id=args['from']).first()
        if not c:
            abort(404)
        outid = c.outputs.filter_by(name=args['out']).first().id
        if not outid:
            abort(404)
        c = Object.query.filter_by(id=args['to']).first()
        if not c:
            abort(404)
        inid = c.inputs.filter_by(name=args['in']).first().id
        if not inid:
            abort(404)
        connection = Connection(inId=inid, outId=outid)
        db.session.add(connection)
        db.session.commit()
        return {'connection': marshal(connection, connection_fields)}, 201


class ConnectionAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('in', type=str, location='json')
        self.reqparse.add_argument('out', type=str, location='json')
        super(ConnectionAPI, self).__init__()

    def get(self, id, api_user):
        connection = Connection.query.filter_by(id=id).first()
        if not connection:
            abort(404)
        return {'connection': marshal(connection, connection_fields)}

    def put(self, api_user):
        args = self.reqparse.parse_args()
        connection = Connection(id=args['id'], inId=args['in'], outId=args['out'])
        db.session.add(connection)
        db.session.commit()
        return {'connection': marshal(connection, connection_fields)}, 201

    def delete(self, id, api_user):
        connection = Connection.query.filter_by(id=id).first()
        if not connection:
            abort(404)
        db.session.delete(connection)
        db.session.commit()
        return {'result': True}


rapi.add_resource(ConnectionListAPI, '/connections')
rapi.add_resource(ConnectionAPI, '/connections/<string:id>')
