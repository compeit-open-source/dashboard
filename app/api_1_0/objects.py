
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

from flask import abort, g
from flask.ext.restful import Resource, reqparse, fields, marshal

from . import rapi
from .authentication import requires_auth
from .. import db
from ..models import Object, Output, Input, User

io_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.String
}

object_fields = {
    'name': fields.String,
    'id': fields.String,
    'description': fields.String,
    'icon': fields.String,
    'user': fields.Integer(attribute='userId'),
    'outputs': fields.List(fields.Nested(io_fields)),
    'inputs': fields.List(fields.Nested(io_fields))
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
        self.reqparse.add_argument('outputs', type=list, location='json')
        self.reqparse.add_argument('inputs', type=list, location='json')
        super(ObjectListAPI, self).__init__()

    def get(self):
        objects = Object.query.all()
        return {'objects': map(lambda t: marshal(t, object_fields), objects)}

    def post(self):
        args = self.reqparse.parse_args()

        # Some kind of input validation, basically copied from below.
        # Maybe should allow incomplete registration if object already exists
        # but that seems less bomb-proof so for now it requires everything.
        if not('name' in args and 'description' in args and 'icon' in args):
            raise ValueError("Invalid object")

        owner = g.current_api_user.id

        # objects do not choose their own ID
        object = Object(userId=owner, roomId=1, name=args['name'], description=args['description'], icon=args['icon'])
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
            if 'name' in input and 'type' in input: # data validation
                db.session.add(Input(objectId=object.id, name=input['name'], type=input['type']))
            else:
                db.session.rollback()
                raise ValueError("Invalid input object")

        db.session.commit()

        return {'object': marshal(object, object_fields)}, 201


class ObjectAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('icon', type=str, location='json')
        super(ObjectAPI, self).__init__()

    def get(self, id):
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        return ({'object': marshal(object, object_fields)})

    def delete(self, id):
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        db.session.delete(object)
        db.session.commit()
        return {'result': True}


class ObjectInputListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(ObjectInputListAPI, self).__init__()

    def get(self, id):
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)
        inputs = []
        for input in object.inputs:
            i = marshal(input, io_fields)
            i['value'] = input_value(input)
            inputs += [i]

        return {'inputs': inputs}


class ObjectInputAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(ObjectInputAPI, self).__init__()

    def get(self, id, name):
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)

        input = object.inputs.filter_by(name=name).first()
        if not input:
            abort(404)

        return input_value(input)


class InputAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(InputAPI, self).__init__()

    def get(self, id):
        input = Input.query.filter_by(id=id).first()
        if not input:
            abort(404)

        #should try and get this working with marshalling instead
        input_json = {'input': marshal(input, io_fields)}
        input_json['input']['value'] = input_value(input)
        return input_json


class OutputAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('value', type=str, location='json')
        super(OutputAPI, self).__init__()

    def post(self, id):
        return self.put(id)

    def put(self, id):
        args = self.reqparse.parse_args()
        output = Output.query.filter_by(id=id).first()
        if not output:
            abort(404)
        output.value = args['value']
        db.session.commit()
        return {'output': marshal(output, value_fields)}


class ObjectOutputAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('value', type=str, location='json')
        super(ObjectOutputAPI, self).__init__()

    def post(self, id, name):
        return self.put(id, name)

    def put(self, id, name):
        args = self.reqparse.parse_args()
        object = Object.query.filter_by(id=id).first()
        if not object:
            abort(404)

        output = object.outputs.filter_by(name=name).first()
        if not output:
            abort(404)

        output.value = args['value']
        db.session.commit()
        return {'output': marshal(output, value_fields)}


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
