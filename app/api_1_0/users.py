
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
from ..models import User

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'name': fields.String
}


class UserListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(UserListAPI, self).__init__()

    def get(self):
        users = User.query.all()
        return {'users': map(lambda t: marshal(t, user_fields), users)}


class UserAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(UserAPI, self).__init__()

    def get(self, id):
        user = User.query.filter_by(id=id).first()
        return {'user': marshal(user, user_fields)}


rapi.add_resource(UserListAPI, '/users')
rapi.add_resource(UserAPI, '/users/<int:id>')
