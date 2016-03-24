
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

from flask import request
from flask.ext.restful import Resource, fields, marshal

from . import rapi
from .authentication import requires_auth
from ..models import FileStorage

file_fields = {
    'type': fields.String,
    'filename': fields.String,
    'url': fields.String,
    'mimetype': fields.String
}

class FileListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(FileListAPI, self).__init__()

    def get(self, api_user):
        files = FileStorage.query.all()
        return {'files': map(lambda t: marshal(t, file_fields), files)}


class FileTypeListAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(FileTypeListAPI, self).__init__()

    def get(self, type, api_user):
        files = FileStorage.query.filter_by(type=type).all()
        return {'files': map(lambda t: marshal(t, file_fields), files)}

    def post(self, type, api_user):
        print request
        # From file uploads
        # parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')


class FilesAPI(Resource):
    decorators = [requires_auth]

    def __init__(self):
        super(FilesAPI, self).__init__()

    def get(self, type, filename, api_user):
        file = FileStorage.query.filter_by(type=type, filename=filename).first()
        return {'file': marshal(file, file_fields)}


rapi.add_resource(FileListAPI, '/files')
rapi.add_resource(FileTypeListAPI, '/files/<string:type>')
rapi.add_resource(FilesAPI, '/files/<string:type>/<string:filename>')
