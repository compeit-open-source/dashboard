
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

from flask import abort, g
from flask.ext.restful import Resource, reqparse, fields, marshal

from . import rapi
from .authentication import requires_auth, requires_auth_token, authenticate
from .. import db
from ..models import Object, ObjectType, Output, Input

import httplib

input_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.String
}

output_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.String,
    'value': fields.String
}

object_fields = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'icon': fields.String,
    'type': fields.Integer,
    'ifttt_maker_event': fields.String,
    'ifttt_maker_trigger_always': fields.Boolean,
    'user': fields.Integer(attribute='userId'),
    'outputs': fields.List(fields.Nested(output_fields)),
    'inputs': fields.List(fields.Nested(input_fields))
}

value_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.String,
    'value': fields.String
}


class ObjectListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('id', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('icon', type=str, location='json')
        self.reqparse.add_argument('type', type=int, location='json')
        self.reqparse.add_argument('ifttt_maker_key', type=str, location='json')
        self.reqparse.add_argument('ifttt_maker_event', type=str, location='json')
        self.reqparse.add_argument('ifttt_maker_trigger_always', type=bool, location='json')
        self.reqparse.add_argument('type', type=int, location='json')
        self.reqparse.add_argument('inputs', type=list, location='json')
        self.reqparse.add_argument('outputs', type=list, location='json')
        self.reqparse.add_argument('inputs', type=list, location='json')
        self.reqparse.add_argument('generate_token', type=bool)
        self.reqparse.add_argument('token_lifetime', type=int)
        super(ObjectListAPI, self).__init__()

    def get(self, api_user):
        objects = Object.query.all()
        return {'objects': map(lambda t: marshal(t, object_fields), objects)}

    def post(self, api_user):
        args = self.reqparse.parse_args()

        # Some kind of input validation, basically copied from below.
        # Maybe should allow incomplete registration if object already exists
        # but that seems less bomb-proof so for now it requires everything.
        if not('name' in args and 'description' in args and 'icon' in args):
            raise ValueError("Invalid object")

        owner = api_user.id

        # objects do not choose their own ID
        object = Object(userId=owner, roomId=None, name=args['name'], description=args['description'], icon=args['icon'])
        db.session.add(object)
        db.session.flush()

        # How will user and room IDs be assigned? - let database do it automatically?

        for output in args['outputs']:
            if 'name' in output and 'type' in output:   # data validation
                db.session.add(Output(objectId=object.id, name=output['name'], type=output['type']))
            else:
                db.session.rollback()
                raise ValueError("Invalid output object")

        for input in args['inputs']:
            if 'name' in input and 'type' in input:  # data validation
                db.session.add(Input(objectId=object.id, name=input['name'], type=input['type']))
            else:
                db.session.rollback()
                raise ValueError("Invalid input object")

        db.session.commit()

        return {'object': marshal(object, object_fields)}, 201


class ObjectAPI(Resource):
    decorators = [requires_auth_token]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('icon', type=str, location='json')
        self.reqparse.add_argument('generate_token', type=bool)
        self.reqparse.add_argument('token_lifetime', type=int)
        super(ObjectAPI, self).__init__()

    def get(self, id, api_user, token):
        args = self.reqparse.parse_args()
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        if not api_user.is_authenticated():
            if not object.confirm_token(token):
                return authenticate()

        ret_obj = marshal(object, object_fields)

        if 'generate_token' in args and args['generate_token']:
            if not api_user.is_authenticated():
                return authenticate()
            if args.token_lifetime:
                new_token = object.generate_token(api_user.id, expiration=args.token_lifetime)
            else:
                new_token = object.generate_token(api_user.id)
            ret_obj['token'] = new_token

        return ({'object': ret_obj})

    def delete(self, id, api_user, token):
        object = Object.query.filter_by(id=id).first()
        if not api_user.is_authenticated():
            return authenticate()
        if not object:
            abort(404)

        db.session.delete(object)
        db.session.commit()
        return {'result': True}


class ObjectInputListAPI(Resource):
    decorators = [requires_auth_token]

    def __init__(self):
        super(ObjectInputListAPI, self).__init__()

    def get(self, id, api_user, token):
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        if not api_user.is_authenticated():
            if not object.confirm_token(token):
                return authenticate()

        inputs = []
        for input in object.inputs:
            i = marshal(input, input_fields)
            i['value'] = input_value(input)
            inputs += [i]

        return {'inputs': inputs}


class ObjectInputAPI(Resource):
    decorators = [requires_auth_token]

    def __init__(self):
        super(ObjectInputAPI, self).__init__()

    def get(self, id, name, api_user, token):
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        if not api_user.is_authenticated():
            if not object.confirm_token(token):
                return authenticate()

        input = object.inputs.filter_by(name=name).first()
        if not input:
            abort(404)

        return input_value(input)


class InputAPI(Resource):
    decorators = [requires_auth_token]

    def __init__(self):
        super(InputAPI, self).__init__()

    def get(self, id, api_user, token):
        input = Input.query.filter_by(id=id).first()
        if not input:
            abort(404)
        if not api_user.is_authenticated():
            if not input.object.confirm_token(token):
                return authenticate()

        input_json = {'input': marshal(input, input_fields)}
        input_json['input']['value'] = input_value(input)
        return input_json


class OutputAPI(Resource):
    decorators = [requires_auth_token]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('value', type=str, location='json')
        super(OutputAPI, self).__init__()

    def post(self, id, api_user, token):
        return self.put(id, api_user, token)

    def put(self, id, api_user, token):
        args = self.reqparse.parse_args()
        output = Output.query.filter_by(id=id).first()
        if not output:
            abort(404)
        if not api_user.is_authenticated():
            if not output.object.confirm_token(token):
                return authenticate()
        change_output_value(output, args['value'])
        return {'output': marshal(output, value_fields)}


class ObjectOutputAPI(Resource):
    decorators = [requires_auth_token]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('value', type=str, location='json')
        super(ObjectOutputAPI, self).__init__()

    def post(self, id, name, api_user, token):
        return self.put(id, name, api_user, token)

    def put(self, id, name, api_user, token):
        args = self.reqparse.parse_args()
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        if not api_user.is_authenticated():
            if not object.confirm_token(token):
                return authenticate()

        output = object.outputs.filter_by(name=name).first()
        if not output:
            abort(404)

        change_output_value(output, args['value'])
        return {'output': marshal(output, value_fields)}


def ifttt_maker_request(event, key, value1=None, value2=None, value3=None):
    headers = {"Content-type": "application/json"}
    params = {}
    if value1:
        params['value1'] = value1
    if value2:
        params['value2'] = value2
    if value3:
        params['value3'] = value3
    # print ('POST', '/trigger/'+event+'/with/key/'+key, json.dumps(params), headers)
    c = httplib.HTTPSConnection('maker.ifttt.com')
    c.request('POST', '/trigger/'+event+'/with/key/'+key, json.dumps(params), headers)
    response = c.getresponse()
    # print response.status
    return response.status == 200


def change_output_value(output, new_value):
    conns = output.connections.all()
    value_changed = output.value != new_value

    output.value = new_value
    db.session.commit()

    for conn in conns:
        obj_input = conn.input
        obj = obj_input.object

        if obj.type == ObjectType.IFTTT_MAKER:
            if not (value_changed or obj.ifttt_maker_trigger_always):
                continue

            if obj.ifttt_maker_event and obj.ifttt_maker_key:
                ifttt_maker_request(obj.ifttt_maker_event, obj.ifttt_maker_key, value1=new_value, value2=obj_input.name, value3=obj.name)


# gets the most up-to-date value for an input from its connected output,
# an input should only have one connection
def input_value(input):
    if any(input.connections):
        outId = input.connections.first().outId
        return Output.query.filter_by(id=outId).first().value
    else:
        return None

rapi.add_resource(ObjectListAPI, '/objects')
rapi.add_resource(ObjectAPI, '/objects/<string:id>')
rapi.add_resource(ObjectInputListAPI, '/objects/<string:id>/inputs')
rapi.add_resource(ObjectInputAPI, '/objects/<string:id>/inputs/<string:name>')
rapi.add_resource(InputAPI, '/inputs/<int:id>')
rapi.add_resource(ObjectOutputAPI, '/objects/<string:id>/outputs/<string:name>')
rapi.add_resource(OutputAPI, '/outputs/<int:id>')
