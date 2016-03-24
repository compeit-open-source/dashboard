# -*- coding: iso-8859-15 -*-

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
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, ValidationError
from wtforms.validators import Required, Email

from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField(u'Remember me')
    submit = SubmitField('Log in')


class RegisterUserForm(Form):
    email = StringField('E-mail', validators=[Required(), Email()])
    name = TextField('Name', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Email()])
    password = PasswordField('New Password', validators=[Required()])
    submit = SubmitField('Reset Password')


class GuestUserForm(Form):
    name = TextField('Name', validators=[Required()])
    submit = SubmitField('Enter')
