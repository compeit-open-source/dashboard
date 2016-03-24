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

import logging
import httplib
import urllib
import random
import string
from random import randint

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask.ext.login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, RegisterUserForm, GuestUserForm, PasswordResetRequestForm, PasswordResetForm
from .. import db
from ..models import User, Circle, StatisticEvent, add_event
from ..email import send_email

'''
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '470154729788964',
        'secret': '010cc08bd4f51e34f3f3e684fbdea8a7'
    }
}

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],  # Facebook does not provide
                                            # username, so the email's user
                                            # is used instead
            me.get('email')
        )
'''

logger = logging.getLogger(__name__)

def create_ia_user(u):
    #print "create_ia_user"
    params = urllib.urlencode({'str': u.iaStorageLocation()+'/'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    if current_app.config['IA_URL'][:5] == 'https':
        # print current_app.config['IA_URL'][8:-1]
        conn = httplib.HTTPSConnection(current_app.config['IA_URL'][8:-1])
    else:
        # print current_app.config['IA_URL'][7:-1]
        conn = httplib.HTTPConnection(current_app.config['IA_URL'][7:-1])
    conn.request("POST", "/PHP/createUser.php", params, headers)
    response = conn.getresponse()
    if response.status == 200:
        logger.debug('Created IA storage')
    else:
        logger.warn('Cannot create IA storage')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    register_form = RegisterUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            add_event(StatisticEvent.USER_LOGIN, userId=user.id)
            if current_app.config['IA_ENABLED'] and not current_app.config['ONLY_IMMERSIVE_SPACE']:
                # hack to create a new user in Information Agent
                create_ia_user(user)

            if request.args.get('next'):
                return redirect(request.args.get('next'))
            elif current_user.defaultRoomId:
                return redirect(url_for('main.room', roomId=current_user.defaultRoomId))
            else:
                return redirect(url_for('main.index'))
        flash('Illegal user or password')

    return render_template('auth/login.html', form=form, register_form=register_form)


@auth.route('/logout')
@login_required
def logout():
    gid = None
    if current_user.guest:
        gid = current_user.id

    if current_user.activeRoomId:
        current_user.activeRoomId = None
        db.session.commit()
    logout_user()
    flash('You have logged out')

    if gid:
        user = User.query.filter_by(id=gid).first()
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('main.index'))


@auth.route('/register', methods=['POST'])
def register_user():
    form = RegisterUserForm()

    if form.validate_on_submit():
        u = User(name=form.name.data, email=form.email.data, password=form.password.data, roleId=1)
        db.session.add(u)
        db.session.commit()
        c = [Circle(name="All", userId=u.id, internal=True), Circle(name="Registered", userId=u.id, internal=True), Circle(name="Friends", userId=u.id), Circle(name="Acquaintances", userId=u.id)]
        db.session.add_all(c)
        db.session.commit()

        if current_app.config['MAIL_CONFIRM']:
            token = u.generate_confirmation_token()
            send_email(u.email, 'Confirm Your Account', 'auth/email/confirm', user=u, token=token)

            flash('A confirmation mail has been sent to you.')
        else:
            u.confirmed = True
            db.session.add(u)
            db.session.commit()

        return redirect(url_for('.login'))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return redirect(url_for('.login'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated() and not current_user.confirmed and not current_user.guest and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed:
        redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent.')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thank you!')
    else:
        flash('The confirmation link is invalid or has expired')

    return redirect(url_for('main.index'))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_authenticated():
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been sent')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if current_user.is_authenticated():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/guest_user/<roomId>', methods=['GET', 'POST'])
def guest_user(roomId):
    form = GuestUserForm()

    if form.validate_on_submit():
	pwd = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        u = User(email=None, name=form.name.data, password=pwd, roleId=1, guest=True)
        db.session.add(u)
        db.session.commit()
        login_user(u, False)
        add_event(StatisticEvent.USER_LOGIN, userId=u.id)

        return redirect(url_for('main.room', roomId=roomId))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return render_template('auth/guest_user.html', form=form)


@auth.route('/check/<member_email>/<circle_name>')
def check(member_email=None, circle_name=None):
    if not request.authorization:
        abort(401)

    auth = request.authorization
    user = User.query.filter_by(email=auth.username).first()
    if not user or not user.verify_password(auth.password):
        abort(401)

    if user_email and circle_name:
        member = User.query.filter_by(email=member_email).first()
        if not member:
            abort(401)
        # implement internal circles?
        cm = CircleMember.query()
        pass
    elif user_email:
        pass

    return '', 200
