
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

import json

from flask import request, jsonify
from flask.ext.restful import Resource, fields, marshal

from . import rapi
from .authentication import requires_auth
from .. import db
from ..models import JSONStorage

json_fields = {
    'type': fields.String,
    'external_id': fields.String(attribute='externalId'),
    'object': fields.String(attribute='json')
}


class JSONListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(JSONListAPI, self).__init__()

    def get(self, api_user):
        objs = JSONStorage.query.all()
        return {'json_objects': map(lambda t: marshal(t, json_fields), objs)}


class JSONTypeListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(JSONTypeListAPI, self).__init__()

    def get(self, type, api_user):
        objs = JSONStorage.query.filter_by(type=type).all()
        return {'json_objects': map(lambda t: marshal(t, json_fields), objs)}


class JSONAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        #self.reqparse = reqparse.RequestParser()
        #self.reqparse.add_argument('type', type=str, location='json')
        #self.reqparse.add_argument('external_id', type=str, location='json')
        #self.reqparse.add_argument('object', type=str, location='json')

        super(JSONAPI, self).__init__()

    def get(self, type, external_id, api_user):
        obj = JSONStorage.query.filter_by(type=type, externalId=external_id).first()
        j = json.loads(obj.json)
        return jsonify(j)

    def post(self, type, external_id, api_user):
        obj = JSONStorage(type=type, externalId=external_id, json=json.dumps(request.json))
        db.session.add(obj)
        db.session.commit()
        return {'json_object': marshal(obj, json_fields)}


rapi.add_resource(JSONListAPI, '/json_store')
rapi.add_resource(JSONTypeListAPI, '/json_store/<string:type>')
rapi.add_resource(JSONAPI, '/json_store/<string:type>/<string:external_id>')
