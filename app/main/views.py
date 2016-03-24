
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

from time import time

from flask import render_template, redirect, url_for, flash, make_response, current_app, request, abort
from flask.json import jsonify
from flask.ext.login import login_required, current_user
from etherpad_lite import EtherpadLiteClient

from . import main
from .forms import UserDefaultRoom
from .. import db, avatars, generator
from ..models import User, Room, RoomAuthorization, RoomPermissions, Widget, EventTypes, FileStorage

def get_available_rooms():
    pass

@main.route('/')
def index():
    return redirect(url_for('.home'))

@main.route('/home')
def home():
    if not current_user.is_authenticated():
        return redirect(url_for('auth.login'))

    if current_user.guest:
        return redirect(url_for('auth.logout'))

    rs = Room.query.order_by('componentId').all()

    form = UserDefaultRoom()

    rc = [('0', 'None')]
    rooms = []
    my_rooms = []
    for room in rs:
        if room.ownerId == current_user.id:
            my_rooms += [room]
            rc += [(str(room.id), room.name)]
        elif room.get_permissions(current_user):
            rooms += [room]
            rc += [(str(room.id), room.name)]

    form.selectRoom.choices = rc
    form.selectRoom.data = str(current_user.defaultRoomId)

    if current_app.config['IA_ENABLED']:
        return render_template('home_ia.html', my_rooms=my_rooms, rooms=rooms, User=User, form=form, avatar_url=avatar_url(current_user), current_user=current_user, current_app=current_app)
    else:
        return render_template('home.html', my_rooms=my_rooms, rooms=rooms, User=User, form=form, avatar_url=avatar_url(current_user), current_user=current_user, current_app=current_app)


@main.route("/set/room", methods=['POST'])
@login_required
def set_room():
    form = UserDefaultRoom()

    rs = Room.query.order_by('componentId').all()

    rc = [('0', 'None')]
    for room in rs:
        if room.ownerId == current_user.id:
            rc += [(str(room.id), room.name)]
        elif room.get_permissions(current_user):
            rc += [(str(room.id), room.name)]

    form.selectRoom.choices = rc

    if form.validate_on_submit():
        if form.selectRoom.data == '0':
            current_user.defaultRoomId = None
        else:
            current_user.defaultRoomId = form.selectRoom.data

        db.session.commit()
        return redirect(url_for('.home'))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return redirect(url_for('.home'))

@main.route('/lobby')
def lobby():
    if not current_user.is_authenticated():
        return redirect(url_for('auth.login'))

    if current_user.guest:
        return redirect(url_for('auth.logout'))

    rs = Room.query.all()

    rooms = []
    for room in rs:
        if get_room_permissions(room, current_user):
            rooms += [room]

    return render_template('lobby.html', rooms=rooms, User=User)

@main.route('/room/<roomId>')
def room(roomId):
    room = Room.query.filter_by(id=roomId).first()

    if not current_user.is_authenticated():
        if room.guest_permission():
            return redirect(url_for('auth.guest_user', roomId=roomId))

        return redirect(url_for('auth.login', next=url_for('.room', roomId=1)))

    cl = room.events.filter_by(type=EventTypes.ROOM_CHAT).order_by('datetime').limit(20)

    return render_template(room.component.template, room=room, chat=cl, current_user=current_user, current_app=current_app)

@login_required
@main.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' in request.files:
        filename = avatars.save(request.files['avatar'])
        url = avatars.url(filename)
        file = FileStorage(type='avatar', filename=current_user.email, url=url)
        db.session.add(file)
        db.session.commit()

    return redirect(url_for('.home'))

def avatar_url(user):
    file = FileStorage.query.filter_by(type='avatar', filename=current_user.email).first()
    if file:
        return file.url
    else:
        return url_for('.identicon', user_id=user.id)

@login_required
@main.route('/avatar/<user_id>')
def identicon(user_id):
    user = User.query.filter_by(id=user_id).first()
    identicon = generator.generate(user.email, 100, 100, output_format='png')
    response = make_response(identicon)
    response.headers["Content-Type"] = "image/png"
    response.headers["Cache-Control"] = "public, max-age=43200"
    return response
