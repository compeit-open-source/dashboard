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

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask.ext.login import UserMixin
from flask import current_app

from . import db
from . import login_manager


class Module(db.Model):
    __table_name__ = 'module'
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    template = db.Column(db.String(64))
    rooms = db.relationship('RoomModule', backref='module', lazy='dynamic')


class Room(db.Model):
    __table_name__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    componentId = db.Column(db.Integer, db.ForeignKey('room_component.id'))
    name = db.Column(db.String(64), unique=True, nullable=False)
    properties = db.Column(db.Text())

    # token = db.Column(db.String(128))
    # tokenValidUnit = db.Column(db.DateTime())

    # users = db.relationship('User', foreign_keys=[id], backref='activeRoom', lazy='dynamic')
    objects = db.relationship('Object', backref='room', lazy='dynamic')
    events = db.relationship('Event', backref='room', lazy='dynamic', cascade='all, delete, delete-orphan')
    circles = db.relationship('RoomAuthorization', backref='room', lazy='dynamic', cascade='all, delete, delete-orphan')
    modules = db.relationship('RoomModule', backref='room', lazy='dynamic', cascade='all, delete, delete-orphan')
    owner = db.relationship('User', foreign_keys=[ownerId], backref='room')
    component = db.relationship('RoomComponent', backref='rooms')

    def generate_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        token = s.dumps({'room': self.id})
        # self.tokenValidUnit = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
        # db.session.add(self)
        return token

    def confirm_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('room') != self.id:
            return False
        return True

    def guest_permission(self):
        if not self.ownerId:
            return 0
        result = 0
        owner = User.query.filter_by(id=self.ownerId).first()
        circles = [owner.circles.filter_by(name='All').first()]
        for circle in circles:
            ra = RoomAuthorization.query.filter_by(roomId=self.id, circleId=circle.id).first()
            if ra:
                result |= ra.permissions

        return result

    def get_permissions(self, user):
        if not self.ownerId or self.ownerId == user.id:
            return RoomPermissions.ADM_ROOM

        # I am sure this can be verified much more optimized but it will have to wait

        # check if the user is a guest
        if user.guest:
            return self.get_permission_guest(self)

        result = 0
        owner = User.query.filter_by(id=self.ownerId).first()
        circles = owner.circles.all()
        for circle in circles:
            for circle_member in circle.members.filter_by(userId=user.id).all():
                ra = RoomAuthorization.query.filter_by(roomId=self.id, circleId=circle.id).first()

                if ra:
                    result |= ra.permissions

        circles = [owner.circles.filter_by(name='All').first()]
        for circle in circles:
            ra = RoomAuthorization.query.filter_by(roomId=self.id, circleId=circle.id).first()
            if ra:
                result |= ra.permissions

        return result


class RoomModule(db.Model):
    __table_name__ = 'room_module'
    id = db.Column(db.Integer, primary_key=True)
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    moduleId = db.Column(db.String(64), db.ForeignKey('module.id'), nullable=False)


class RoomComponent(db.Model):
    __table_name__ = 'room_component'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    template = db.Column(db.String(64))


class RoomPermissions:
    ADM_CIRCLES = 0x01
    ADM_MODULES = 0x02
    ADM_OBJECTS = 0x4
    ADM_ROOM = 0xFF


class RoomAuthorization(db.Model):
    __table_name__ = 'room_authorization'
    id = db.Column(db.Integer, primary_key=True)
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    circleId = db.Column(db.Integer, db.ForeignKey('circle.id'), nullable=False)
    permissions = db.Column(db.Integer)

    db.UniqueConstraint('roomId', 'circleId')


class Widget(db.Model):
    __table_name__ = 'widget'
    id = db.Column(db.Integer, primary_key=True)
    componentId = db.Column(db.Integer, db.ForeignKey('room_component.id'))
    title = db.Column(db.String())
    name = db.Column(db.String())
    title = db.Column(db.String())
    controller = db.Column(db.String())
    constr = db.Column(db.String())
    icon = db.Column(db.String())
    stylesheet = db.Column(db.String())
    template = db.Column(db.String())
    opts = db.Column(db.Text)


class ObjectType:
    GENERIC = 0
    IFTTT_MAKER = 1


class Object(db.Model):
    __table_name__ = 'object'
    id = db.Column(db.Integer, primary_key=True)
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followUser = db.Column(db.Integer, default=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text())
    icon = db.Column(db.String())
    token = db.Column(db.String(128))
    tokenValidUnit = db.Column(db.DateTime())
    # add last seen/active variable?

    type = db.Column(db.Integer)
    ifttt_maker_key = db.Column(db.String())
    ifttt_maker_event = db.Column(db.String())
    ifttt_maker_trigger_always = db.Column(db.Boolean, default=True)

    inputs = db.relationship('Input', backref='object', lazy='dynamic', cascade='all, delete, delete-orphan')
    outputs = db.relationship('Output', backref='object', lazy='dynamic', cascade='all, delete, delete-orphan')
    circles = db.relationship('ObjectAuthorization', backref='object', lazy='dynamic', cascade='all, delete, delete-orphan')

    def generate_token(self, user_id, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'object_id': self.id, 'user_id': user_id})
        # self.tokenValidUnit = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
        # db.session.add(self)

    def confirm_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        if data.get('object_id') != self.id:
            return None
        return data.get('user_id')


class ObjectPermissions:
    READ = 0x01
    WRITE = 0x02


class ObjectAuthorization(db.Model):
    __table_name__ = 'object_authorization'
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer, db.ForeignKey('object.id'), nullable=False)
    circleId = db.Column(db.Integer, db.ForeignKey('circle.id'), nullable=False)
    permissions = db.Column(db.Integer)

    db.UniqueConstraint('objectId', 'circleId')


class Input(db.Model):
    __table_name__ = 'input'
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer, db.ForeignKey('object.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)

    connections = db.relationship('Connection', backref='input', lazy='dynamic', cascade="all, delete, delete-orphan")


class Output(db.Model):
    __table_name__ = 'output'
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer, db.ForeignKey('object.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(64))

    connections = db.relationship('Connection', backref='output', lazy='dynamic', cascade="all, delete, delete-orphan")


class Connection(db.Model):
    __table_name__ = 'connection'
    id = db.Column(db.Integer, primary_key=True)
    inId = db.Column(db.Integer, db.ForeignKey('input.id', ondelete='CASCADE'), nullable=False)
    outId = db.Column(db.Integer, db.ForeignKey('output.id', ondelete='CASCADE'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permissions:
    VIEW_USERS = 0x01
    VIEW_ROOMS = 0x02
    ADM_USERS = 0x04
    ADM_ROOMS = 0x08


class Role(db.Model):
    __table_name__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, default=0)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role Id: %d, Name %s, Permissions: 0x%x>' % (self.id, self.name, self.permissions)


class User(UserMixin, db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64), nullable=False)
    roleId = db.Column(db.Integer, db.ForeignKey('role.id'), default=1, nullable=True)
    activeRoomId = db.Column(db.Integer, db.ForeignKey('room.id', use_alter=True, name='fk_room_id'), default=None)
    # iaStorageLocation = db.Column(db.String(), nullable=True)
    guest = db.Column(db.Boolean(), default=False)
    confirmed = db.Column(db.Boolean(), default=False)
    defaultRoomId = db.Column(db.Integer, db.ForeignKey('room.id', use_alter=True, name='def_room_id'), default=None)
    avatar = db.Column(db.String(256), nullable=True)

    circles = db.relationship('Circle', backref='user', lazy='dynamic', cascade='all, delete, delete-orphan')
    objects = db.relationship('Object', backref='user', lazy='dynamic', cascade='all, delete, delete-orphan')
    circle_member = db.relationship('CircleMember', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # chat = db.relationship('Chat', backref='user', foreign_keys=[UserId], lazy='dynamic', cascade='all, delete, delete-orphan')
    # defaultRoom = db.relationship('Room', foreign_keys=[defaultRoomId], backref='defaultUsers')
    # rooms = db.relationship('Room', backref='owner', lazy='dynamic', foreign_keys=[], cascade='all, delete, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def iaStorageLocation(self):
        return self.password_hash[-10:]

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.roleId is None:
            self.roleId = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return "User(email=%r, password_hash=%r, name=%r, roleId=%d)" % (self.email, self.password_hash, self.name, self.roleId)

    def active(self):
        return self.activeRoomId is not None

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'name': self.name}


class Circle(db.Model):
    __table_name__ = 'circle'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(64))
    internal = db.Column(db.Boolean, default=False)

    members = db.relationship('CircleMember', backref='circle', lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "Circle(userId=%d, name=%r)" % (self.userId, self.name)


class CircleMember(db.Model):
    __table_name__ = 'circle_member'
    id = db.Column(db.Integer, primary_key=True)
    circleId = db.Column(db.Integer, db.ForeignKey('circle.id'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "CircleMember(circleId=%d, userId=%d)" % (self.circleId, self.userId)


class EventTypes:
    ROOM_EVENT = 1
    USER_EVENT = 2
    ROOM_CHAT = 3
    USER_CHAT = 4


class Event(db.Model):
    __table_name__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    toUser = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64))
    datetime = db.Column(db.DateTime())
    text = db.Column(db.Text())


class FileStorageAuthorization(db.Model):
    __table_name__ = 'object_authorization'
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer, db.ForeignKey('file_storage.id'), nullable=False)
    circleId = db.Column(db.Integer, db.ForeignKey('circle.id'), nullable=False)
    permissions = db.Column(db.Integer)

    db.UniqueConstraint('objectId', 'circleId')


class FileStorage(db.Model):
    __table_name__ = 'file_storage'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(), nullable=False)
    type = db.Column(db.String())
    mimetype = db.Column(db.String(), nullable=True)
    url = db.Column(db.Text())
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    db.UniqueConstraint('filename', 'type')

    def __repr__(self):
        return "FileStorage(id=%d, type=%s, filename=%s, url=%s, userId=%d, mimetype=%s)" % (self.id, self.type, self.filename, self.url, self.userId if self.userId else -1, self.mimetype)

    def to_dict(self):
        d = {'id': self.id, 'type': self.type, 'filename': self.filename, 'url': self.url, 'mimetype': self.mimetype}
        if self.userId:
            d['userId'] = self.userId
        return d


class JSONStorageAuthorization(db.Model):
    __table_name__ = 'json_authorization'
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer, db.ForeignKey('json_storage.id'), nullable=False)
    circleId = db.Column(db.Integer, db.ForeignKey('circle.id'), nullable=False)
    permissions = db.Column(db.Integer)

    db.UniqueConstraint('objectId', 'circleId')


class JSONStorage(db.Model):
    __table_name__ = 'json_storage'
    id = db.Column(db.Integer, primary_key=True)
    externalId = db.Column(db.String())
    type = db.Column(db.String())
    json = db.Column(db.Text())
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    db.UniqueConstraint('externalId', 'type')


class StatisticEvent:
    SYSTEM_START = 1
    SYSTEM_STOP = 2
    USER_LOGIN = 3
    USER_LOGOUT = 4
    ROOM_JOIN = 5
    ROOM_LEAVE = 6
    API_CALL = 7
    MODULE_EVENT = 8


class Statistic(db.Model):
    __table_name__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime())
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    event = db.Column(db.Integer())
    module = db.Column(db.String(), nullable=True)


def add_event(event, userId=None, roomId=None, module=None):
    if current_app.config['STATISTICS']:
        db.session.add(Statistic(datetime=datetime.utcnow(), userId=userId, roomId=roomId, event=event, module=module))
        db.session.commit()


def create_sample_db():
    # example DB entries
    roles = [Role(name='User', default=True),
             Role(name=u'Administrator', permissions=0xFF)]

    users = [User(email=u'nogge1@test.com', password_hash=u'pbkdf2:sha1:1000$KA73jih2$72a12150794d2e8b62cc303d62ea6430921a62cd', name=u'Joakim Norrgard1', roleId=1, confirmed=True),
             User(email=u'nogge2@test.com', password_hash=u'pbkdf2:sha1:1000$URtyTjXj$2d1ad7fdb8320687157ab288469a98f0b3d6aea0', name=u'Joakim Norrgard2', roleId=3, confirmed=True)]

    circles = [Circle(name="All", userId=1, internal=True)]
    circles += [Circle(name="All", userId=2, internal=True)]
    circles += [Circle(userId=1, name=u'Family'),
                Circle(userId=1, name=u'Friends'),
                Circle(userId=1, name=u'Acquaintances')]

    circle_members = [CircleMember(circleId=1, userId=2),
                      CircleMember(circleId=2, userId=2)]

    room_components = [RoomComponent(id=1, name='Simple', template='components/simple.html')]

    rooms = [Room(id=1, name='Simple Example', ownerId=None, componentId=1)]

    room_auth = [RoomAuthorization(circleId=1, roomId=1, permissions=0xFF),
                 RoomAuthorization(circleId=2, roomId=1, permissions=0xFF)]

    objects = [Object(id=1, roomId=1, userId=1, name='Desk light', icon='/static/img/hue.png', description='Nice lamp on the desk'),
               Object(id=2, roomId=1, userId=1, name='Motion detector', icon='/static/img/lilpoly.png', description='Motion detector in my room'),
               Object(id=3, roomId=1, userId=1, name='Maker Output', icon='', description='Maker Output'),
               Object(id=4, roomId=1, userId=1, name='Maker Input', icon='', description='Maker Input', type=1, ifttt_maker_event='send_mail', ifttt_maker_trigger_always=True, ifttt_maker_key='')]

    object_auth = [ObjectAuthorization(circleId=1, objectId=1, permissions=3),
                   ObjectAuthorization(circleId=2, objectId=1, permissions=3)]

    outputs = [Output(id=1, objectId=2, name='Motion', type='bool', value='True'),
               Output(id=2, objectId=3, name='output', type='str', value='Hello')]

    inputs = [Input(id=1, objectId=1, name='Toggle', type='bool'),
              Input(id=2, objectId=4, name='input', type='str')]

    connections = [Connection(id=1, inId=1, outId=1),
                   Connection(id=2, inId=2, outId=2)]

    db.drop_all()
    db.create_all()
    db.session.add_all(roles)
    db.session.add_all(users)
    db.session.add_all(circles)
    db.session.add_all(circle_members)
    db.session.add_all(room_components)
    db.session.add_all(rooms)
    db.session.add_all(room_auth)
    db.session.add_all(objects)
    db.session.add_all(object_auth)
    db.session.add_all(outputs)
    db.session.add_all(inputs)
    db.session.add_all(connections)
    db.session.commit()
