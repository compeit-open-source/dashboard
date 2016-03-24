
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

from functools import wraps

from flask import g, request, make_response, jsonify
from flask.ext.login import current_user

from ..models import User


def check_auth(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return None

    #move to decorator
    setattr(g, 'current_api_user', user)

    return user


def authenticate():
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated():
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
        return f(*args, **kwargs)
    return decorated
