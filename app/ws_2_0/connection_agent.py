
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

from flask import request
from flask.ext.login import login_required, current_user
from flask.ext.socketio import emit, join_room, leave_room

from .. import socketio, db
from ..models import User, StatisticEvent
from ..models import add_event

import kurento_agent
import chat_agent
import file_agent

logger = logging.getLogger(__name__)

# WS Socket communication

ws_clients = {}


def user_emit(user_id, event, data):
    if int(user_id) in ws_clients:
        ws_clients[int(user_id)]['/connection_agent'].base_emit(event, data)
    else:
        print ws_clients
        logger.info('User id '+user_id+' not among connected ws clients')


@socketio.on('connect', namespace='/connection_agent')
@login_required
def dashboard_connect():
    logger.debug('Got ws connect user id: %d with session id: %s' % (current_user.id, request.namespace.socket.sessid))

    ws_clients[int(current_user.id)] = request.namespace.socket
    emit('connected', {'user': {'id': current_user.id, 'name': current_user.name}})


@socketio.on('join_room', namespace='/connection_agent')
def room_join(message):
    roomId = int(message['room'])
    logger.debug("got join_room for " + str(roomId))

    logger.debug(request.namespace.socket.sessid)

    if current_user.activeRoomId and int(current_user.activeRoomId) != int(roomId):
        logger.debug("leaving room " + str(current_user.activeRoomId) + " to room " + str(roomId))
        join_room(current_user.activeRoomId)
        emit('user_left', {'user': current_user.to_dict()}, room=int(current_user.activeRoomId))
        add_event(StatisticEvent.ROOM_LEAVE, userId=current_user.id, roomId=roomId)
        leave_room(current_user.activeRoomId)

    emit('room_joined')

    emit('user_joined', {'user': current_user.to_dict()}, room=roomId)
    add_event(StatisticEvent.ROOM_JOIN, userId=current_user.id, roomId=roomId)

    join_room(roomId)
    if not current_user.activeRoomId or int(current_user.activeRoomId) != int(roomId):
        current_user.activeRoomId = roomId
        db.session.commit()

    active_users = User.query.filter_by(activeRoomId=roomId).all()

    for user in active_users:
        if current_user.id != user.id and user.id in ws_clients:
            user_emit(current_user.id, 'user_joined', {'user': user.to_dict()})


@socketio.on('leave_room', namespace='/connection_agent')
def room_leave(message):
    if current_user.activeRoomId:
        roomId = current_user.activeRoomId
        emit('user_left', {'user': current_user.to_dict()}, room=roomId)
        leave_room(roomId)
        add_event(StatisticEvent.ROOM_LEAVE, userId=current_user.id, roomId=roomId)

    current_user.activeRoomId = None
    db.session.commit()

    emit('room_left', {})


@socketio.on('disconnect', namespace='/connection_agent')
@login_required
def dashboard_disconnect():
    if request.namespace.socket.sessid == ws_clients[current_user.id].sessid:
        if current_user.activeRoomId:
            emit('user_left', {'user': current_user.to_dict()}, room=int(current_user.activeRoomId))
            add_event(StatisticEvent.ROOM_LEAVE, userId=current_user.id, roomId=current_user.activeRoomId)

        current_user.activeRoomId = None
        db.session.commit()
        logger.debug('Client disconnected')
    else:
        logger.debug('Old session disconnected')


@socketio.on('server_message', namespace='/connection_agent')
def server_message(message):
    logger.debug('server_message(' + str(current_user.activeRoomId) + ') ' + str(message))

    if 'type' in message:
        if message['type'] == 'kurento':
            kurento_agent.server_message(message['data'])
        elif message['type'] == 'file':
            file_agent.server_message(message['data'])


@socketio.on('room_message', namespace='/connection_agent')
def room_message(message):
    logger.debug('room_message' + str(message) + ' (' + str(current_user.activeRoomId)+')')

    # Special message types

    if 'type' in message and message['type'] == 'chat':
        chat_agent.room_message(message)

    emit('room_message', {'user': current_user.to_dict(), 'type': message['type'], 'data': message['data']}, room=int(current_user.activeRoomId))


@socketio.on('user_message', namespace='/connection_agent')
def user_message(message):
    logger.debug('user_message' + str(message) + ' (' + str(current_user.activeRoomId)+')')

    if 'type' in message and message['type'] == 'chat':
        chat_agent.user_message(message)

    if 'to' in message and int(message['to']) in ws_clients:
        user_emit(message['to'], 'user_message', {'type': message['type'], 'data': message['data'], 'from': current_user.id})
