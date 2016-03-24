
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

from flask.ext.wtf import Form
from wtforms import SubmitField, TextField, PasswordField, SelectField
from wtforms.validators import Required


class AddCircleForm(Form):
    name = TextField('Name', validators=[Required()])
    submit = SubmitField('Add')


class AdmUserForm(Form):
    email = TextField('Email', validators=[Required()])
    name = TextField('Name', validators=[Required()])
    password = PasswordField('Password')
    submit = SubmitField('Save')


class AdmRoomForm(Form):
    name = TextField('Name', validators=[Required()])
    selectComponent = SelectField('Type')
    submit = SubmitField('Save')
