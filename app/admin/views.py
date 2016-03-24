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

from flask import render_template, redirect, url_for, flash, current_app
from flask.ext.login import login_required, current_user

from . import admin
from .forms import AdmUserForm, AdmRoomForm, AddCircleForm
from .. import db
from ..models import User, Object, Connection, Room, Circle, CircleMember, ObjectAuthorization, RoomAuthorization, RoomModule, Module, RoomComponent


@admin.route("/circles")
@login_required
def circles():
    form = AddCircleForm()

    c = current_user.circles.all()
    c = c[2:]
    u = User.query.all()

    cm_matrix = []
    for user in u:
        cm_array = [user.name+' ('+user.email+')']
        for circle in c:
            cm = CircleMember.query.filter_by(circleId=circle.id, userId=user.id).first()
            cm_array += [(circle.id, user.id, cm is not None)]
        cm_matrix += [cm_array]

    # print cm_matrix

    return render_template('admin/circles.html', circles=c, users=u, members=cm_matrix, form=form)


@admin.route("/add/circle", methods=['POST'])
@login_required
def add_circle():
    form = AddCircleForm()

    if form.validate_on_submit():
        c = Circle(name=form.name.data, userId=current_user.id)
        db.session.add(c)
        db.session.commit()
        flash(u"New circle added")

        return redirect(url_for('.circles'))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return redirect(url_for('.circles'))


@admin.route("/delete/circle/<circleId>")
@login_required
def delete_circle(circleId):
    c = Circle.query.filter_by(id=circleId).first()
    if c and c.userId == current_user.id:
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for('.circles'))


@admin.route("/add/circle_member/<circleId>/<userId>")
@login_required
def add_circle_member(circleId, userId):
    c = Circle.query.filter_by(id=circleId).first()
    u = User.query.filter_by(id=userId).first()
    if c and u and c.userId == current_user.id:
        db.session.add(CircleMember(circleId=c.id, userId=u.id))
        db.session.commit()

    return redirect(url_for('.circles'))


@admin.route("/delete/circle_member/<circleId>/<userId>")
@login_required
def delete_circle_member(circleId, userId):
    c = Circle.query.filter_by(id=circleId).first()
    cm = CircleMember.query.filter_by(circleId=circleId, userId=userId).first()
    if cm and c.userId:
        db.session.delete(cm)
        db.session.commit()
    return redirect(url_for('.circles'))


@admin.route("/rooms")
@login_required
def rooms():
    form = AdmRoomForm()

    c = current_user.circles.all()
    r = Room.query.filter_by(ownerId=current_user.id).all()
    tc = [(str(t.id), t.name) for t in RoomComponent.query.all()]
    form.selectComponent.choices = tc

    ra_matrix = []
    for room in r:
        ra_array = [room.name]
        for circle in c:
            ra = RoomAuthorization.query.filter_by(circleId=circle.id, roomId=room.id).first()
            if ra:
                ra_array += [(circle.id, room.id, ra.permissions)]
            else:
                ra_array += [(circle.id, room.id, None)]
        ra_matrix += [ra_array]

    m = Module.query.all()

    rm_matrix = []
    for room in r:
        rm_array = [(room.name, room.id, room.component.name if room.component else 'None')]
        for module in m:
            rm = RoomModule.query.filter_by(moduleId=module.id, roomId=room.id).first()
            rm_array += [(module.id, room.id, rm is not None)]
        rm_matrix += [rm_array]

    return render_template('admin/rooms.html', form=form, rooms=rm_matrix, circles=c, authorizations=ra_matrix, modules=m)


@admin.route("/add/room", methods=['GET', 'POST'])
@login_required
def add_room(userId=None):
    form = AdmRoomForm()

    tc = [(str(t.id), t.name) for t in RoomComponent.query.all()]
    form.selectComponent.choices = tc

    if form.validate_on_submit():
        r = Room(ownerId=current_user.id, name=form.name.data, componentId=form.selectComponent.data)
        db.session.add(r)
        db.session.commit()
        flash(u"New room added")

        return redirect(url_for('.rooms'))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return redirect(url_for('.rooms'))


@admin.route("/delete/room/<roomId>")
@login_required
def delete_room(roomId):
    r = Room.query.filter_by(id=roomId).first()
    if r and r.ownerId == current_user.id:
        db.session.delete(r)
        db.session.commit()
    return redirect(url_for('.rooms'))


@admin.route("/add/room_module/<moduleId>/<roomId>")
@login_required
def add_room_module(moduleId, roomId):
    m = Module.query.filter_by(id=moduleId).first()
    r = Room.query.filter_by(id=roomId).first()
    if m and r and r.ownerId == current_user.id:
        db.session.add(RoomModule(moduleId=m.id, roomId=r.id))
        db.session.commit()

    return redirect(url_for('.rooms'))


@admin.route("/delete/room_module/<moduleId>/<roomId>")
@login_required
def delete_room_module(moduleId, roomId):
    r = Room.query.filter_by(id=roomId).first()
    rm = RoomModule.query.filter_by(moduleId=moduleId, roomId=roomId).first()
    if rm and r.ownerId == current_user.id:
        db.session.delete(rm)
        db.session.commit()
    return redirect(url_for('.rooms'))


@admin.route("/add/room_authorization/<circleId>/<roomId>")
@login_required
def add_room_authorization(circleId, roomId):
    c = Circle.query.filter_by(id=circleId).first()
    r = Room.query.filter_by(id=roomId).first()
    if c and r and r.ownerId == current_user.id:
        db.session.add(RoomAuthorization(circleId=c.id, roomId=r.id, permissions=0xFF))
        db.session.commit()

    return redirect(url_for('.rooms'))


@admin.route("/delete/room_authorization/<circleId>/<roomId>")
@login_required
def delete_room_authorization(circleId, roomId):
    r = Room.query.filter_by(id=roomId).first()
    rm = RoomAuthorization.query.filter_by(circleId=circleId, roomId=roomId).first()
    if rm and r.ownerId == current_user.id:
        db.session.delete(rm)
        db.session.commit()
    return redirect(url_for('.rooms'))


@admin.route("/users")
@login_required
def users():
    u = User.query.all()
    form = AdmUserForm()

    return render_template('admin/users.html', form=form, users=u)


@admin.route("/add/user", methods=['GET', 'POST'])
@login_required
def add_user(userId=None):
    form = AdmUserForm()

    if form.validate_on_submit():
        u = User(email=form.email.data, name=form.name.data, password=form.password.data, roleId=1)
        db.session.add(u)
        db.session.commit()
        flash(u"New user added")

        return redirect(url_for('.users'))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return redirect(url_for('.users'))


@admin.route("/user/<userId>", methods=['GET', 'POST'])
@login_required
def edit_user(userId=None):
    u = User.query.filter_by(id=userId).first()

    if u.id != current_user.id:
        return redirect(url_for('.users'))

    form = AdmUserForm()

    if form.validate_on_submit():
        u.email = form.email.data
        u.name = form.name.data
        #if form.iaSL.data:
        #    u.iaStorageLocation = form.iaSL.data
        #else:
        #    u.iaStorageLocation = None
        if form.password.data:
            u.password = form.password.data
        db.session.commit()
        flash('User saved')

        return redirect(url_for('.users'))
    else:
        for form_error in form.errors:
            for field_error in form[form_error].errors:
                flash(form[form_error].label.text+" - "+field_error, 'error')

    return redirect(url_for('.users'))


@admin.route("/delete/user/<userId>")
@login_required
def delete_user(userId):
    u = User.query.filter_by(id=userId).first()
    if u and u.id == current_user.id:
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for('.users'))


@admin.route("/objects")
@login_required
def objects():
    c = current_user.circles.all()
    comps = Object.query.filter_by(userId=current_user.id).all()
    conns = Connection.query.all()

    ca_matrix = []
    for object in comps:
        ca_array = [(0, 0, object.name)]
        for circle in c:
            ca = ObjectAuthorization.query.filter_by(circleId=circle.id, objectId=object.id).first()
            if ca:
                ca_array += [(circle.id, object.id, ca.permissions)]

            else:
                ca_array += [(circle.id, object.id, None)]
        ca_matrix += [ca_array]

    # print ca_matrix

    return render_template('admin/objects.html', objects=comps, connections=conns, circles=c, authorizations=ca_matrix)
