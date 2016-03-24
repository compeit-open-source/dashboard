
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

from . import rapi
from .authentication import requires_auth
from .. import db
from ..models import User, Circle, CircleMember

member_fields = {
    'id': fields.Integer,
    'email': fields.String(attribute='user.email'),
    'name': fields.String(attribute='user.name'),
}

circle_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'members': fields.List(fields.Nested(member_fields))
}

membercircle_fields = {
    'id': fields.Integer,
    'name': fields.String
}


class CircleAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(CircleAPI, self).__init__()

    def get(self, id, api_user):
        circle = api_user.circles.filter_by(id=id).first()
        return {'circle': marshal(circle, circle_fields)}

    def put(self, api_user):
        args = self.reqparse.parse_args()
        circle = Circle(name=args['name'])
        db.session.add(circle)
        db.session.commit()
        return {'circle': marshal(circle, circle_fields)}, 201


class CircleListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(CircleListAPI, self).__init__()

    def get(self, api_user):
        circles = api_user.circles.all()
        return {'circles': map(lambda t: marshal(t, circle_fields), circles)}


class MemberCirclesAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(MemberCirclesAPI, self).__init__()

    def get(self, id, api_user):
        # can probably be optimized by a SQL join search, or better relationships
        circles = api_user.circles.filter_by()
        result = []
        for circle in circles:
            # todo: implement the members of the internal circles...
            if not circle.internal:
                circle_member = circle.members.filter_by(userId=id).first()
                if circle_member:
                    result.append(marshal(circle, membercircle_fields))
        return {'circles': result}


rapi.add_resource(CircleAPI, '/circle/<int:id>')
rapi.add_resource(CircleListAPI, '/circles')
rapi.add_resource(MemberCirclesAPI, '/circles/user/<int:id>')
