
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

from flask import request, make_response, jsonify
from flask.ext.login import current_user, AnonymousUserMixin

from ..models import User, StatisticEvent
from ..models import add_event


def check_auth(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return None
    return user


def authenticate():
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_user = None
        if not current_user.is_authenticated():
            auth = request.authorization
            if auth:
                api_user = check_auth(auth.username, auth.password)
            if not auth or not api_user:
                return authenticate()
        else:
            api_user = current_user

        add_event(StatisticEvent.API_CALL, userId=api_user.id)

        return f(*args, api_user=api_user, **kwargs)
    return decorated


def requires_auth_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_user = None
        if not current_user.is_authenticated() and not request.args.get('token'):
            auth = request.authorization
            if auth:
                api_user = check_auth(auth.username, auth.password)

            if not auth or not api_user:
                return authenticate()
        else:
            api_user = current_user

        # if not issubclass(api_user, AnonymousUserMixin):
        #    add_event(StatisticEvent.API_CALL, userId=api_user.id)

        return f(*args, api_user=api_user, token=request.args.get('token'), **kwargs)
    return decorated
