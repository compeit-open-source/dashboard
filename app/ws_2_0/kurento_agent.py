
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
from flask.ext.socketio import emit
from flask.ext.login import current_user

from ..models import User

from ..pykurento import KurentoClient
from ..pykurento import media

logger = logging.getLogger(__name__)


# Kurento client
# kurento = KurentoClient("ws://192.168.77.244:8888/kurento")
kurento = KurentoClient("ws://ice.compeit.eu:8888/kurento")
sessions = {}
candidatesQueue = {}
senders = {}
pipeline = None
sessionIds = {}

# WS Socket communication

ws_client = None


def on_media_started(wrtc, value, cb_args):
    from connection_agent import user_emit
    user_id = cb_args['user_id']
    data = {}
    if 'sender_id' in cb_args:
        data['sender'] = cb_args['sender_id']
    user_emit(user_id, 'server_message', {'type': 'kurento', 'event': 'media_session_started', 'data': data})


def on_media_terminated(wrtc, value, cb_args):
    from connection_agent import user_emit
    user_id = cb_args['user_id']
    data = {}
    if 'sender_id' in cb_args:
        data['sender'] = cb_args['sender_id']
    user_emit(user_id, 'server_message', {'type': 'kurento', 'event': 'media_session_terminated', 'data': data})


def on_ice_candidate_server(wrtc, value, cb_args):
    from connection_agent import user_emit

    user_id = cb_args['user_id']
    candidate = value['data']['candidate']
    data = {'candidate': {'candidate': candidate['candidate'], 'sdpMLineIndex': candidate['sdpMLineIndex'], 'sdpMid': candidate['sdpMid']}}

    if 'sender_id' in cb_args:
        data['sender'] = cb_args['sender_id']

    user_emit(user_id, 'server_message', {'type': 'kurento', 'event': 'on_ice_candidate', 'data': data})


def on_ice_candidate_client(msg):
    if 'sender' in msg:
        logger.debug(senders)
        sender = senders[str(msg['sender'])]
        wrtc = sender['receivers'][str(current_user.id)]
    else:
        sender = senders[str(current_user.id)]
        wrtc = sender['endpoint']

    wrtc.add_ice_candidate(msg['candidate'])


def send_start(msg):
    global pipeline

    sessionId = request.namespace.socket.sessid

    logger.debug('Connection ' + sessionId + 'received send_start')
    # logger.debug(str(msg))
    sdp_offer = msg['offerSdp']
    if not pipeline:
        pipeline = kurento.create_pipeline()
    wrtc = media.WebRtcEndpoint(pipeline)
    senders[str(current_user.id)] = {'sid': sessionId, 'pipeline': pipeline, 'endpoint': wrtc, 'receivers': {}}

    wrtc.on_ice_candidate(on_ice_candidate_server, user_id=current_user.id)
    wrtc.on_media_session_started_event(on_media_started, user_id=current_user.id)
    wrtc.on_media_session_terminated_event(on_media_terminated, user_id=current_user.id)

    sdp_answer = wrtc.process_offer(sdp_offer)

    wrtc.gather_candidates()

    emit('server_message', {'type': 'kurento', 'event': 'send_started', 'data': {'sdp_answer': sdp_answer}})

    # emit('av_available', {'sender': current_user.id}, room=current_user.activeRoomId)


def send_stop(msg):
    from connection_agent import user_emit
    global pipeline

    sessionId = request.namespace.socket.sessid

    logger.debug('Connection ' + sessionId + 'received send_stop')
    logger.debug(str(msg))
    sender = senders.pop(str(current_user.id), None)
    for user_id in sender['receivers']:
        user_emit(user_id, 'server_message', {'type': 'kurento', 'event': 'sender_stopped'})
        sender['receivers'][user_id].release()

    if sender:
        sender['endpoint'].release()

    emit('server_message', {'type': 'kurento', 'event': 'send_stopped'})

    # emit('av_not_available', {'sender': current_user.id}, room=current_user.activeRoomId)


def av_available():
    pass


def receive_start(message):
    global pipeline
    sessionId = request.namespace.socket.sessid

    logger.debug('Connection ' + sessionId + ' received receive_start')
    logger.debug(str(message))
    sdp_offer = message['offerSdp']
    if not pipeline:
        pipeline = kurento.create_pipeline()
    wrtc = media.WebRtcEndpoint(pipeline)
    logger.debug(senders)
    sender = senders[str(message['sender'])]
    sender['receivers'][str(current_user.id)] = wrtc

    sdp_answer = wrtc.process_offer(sdp_offer)

    sender['endpoint'].connect(wrtc)

    wrtc.on_ice_candidate(on_ice_candidate_server, user_id=current_user.id, sender_id=message['sender'])
    wrtc.on_media_session_started_event(on_media_started, user_id=current_user.id, sender_id=message['sender'])
    wrtc.on_media_session_terminated_event(on_media_terminated, user_id=current_user.id, sender_id=message['sender'])
    wrtc.gather_candidates()

    emit('server_message', {'type': 'kurento', 'event': 'receive_started', 'data': {'sdp_answer': sdp_answer, 'sender': message['sender']}})


def receive_stop(message):
    global pipeline

    sessionId = request.namespace.socket.sessid

    logger.debug('Connection ' + sessionId + 'received receive_stop')
    # logger.debug(str(msg))

    sender = senders[str(message['sender'])]
    receiver = sender['receivers'].pop(str(current_user.id))

    if receiver:
        receiver.release()

    if not sender['receivers']:
        sender['endpoint'].release()
        senders.pop(str(message['sender']), None)

    emit('server_message', {'type': 'kurento', 'event': 'receive_stopped', 'data': {'sender': message['sender']}})


def server_message(msg):
    if 'event' in msg:
        if msg['event'] == 'send_start':
            send_start(msg)
        elif msg['event'] == 'send_stop':
            send_stop(msg)
        elif msg['event'] == 'receive_start':
            receive_start(msg)
        elif msg['event'] == 'receive_stop':
            receive_stop(msg)
        elif msg['event'] == 'on_ice_candidate':
            on_ice_candidate_client(msg)

# Kurento examples (currently not used)
# presenter

def presenter_start(msg):
    global presenter

    sessionId = request.namespace.socket.sessid
    message = json.loads(msg)
    logger.debug('Connection ' + sessionId + ' received message ' + str(message))
    sdp_offer = message['sdpOffer']
    pipeline = kurento.create_pipeline()
    wrtc = media.WebRtcEndpoint(pipeline)
    sessions[sessionId] = wrtc
    presenter = {'sid': sessionId, 'pipeline': pipeline, 'endpoint': wrtc}

    # wrtc.on_media_session_started_event(on_event)
    # wrtc.on_media_session_terminated_event(on_event)

    sdp_answer = wrtc.process_offer(sdp_offer)

    wrtc.gather_candidates()

    emit('presenterResponse', {'id': 'presenterResponse', 'response': 'accepted', 'sdpAnswer': sdp_answer})


def presenter_stop(msg):
    global presenter

    if presenter:
        emit('stopCommunication', {'id': 'stopCommunication'}, room=int(current_user.activeRoomId))

        presenter['pipeline'].release()
        presenter = None


def presenter_viewer(msg):
    global presenter
    sessionId = request.namespace.socket.sessid

    message = json.loads(msg)
    logger.debug('Connection ' + sessionId + ' received message ' + str(message))
    logger.debug(presenter)
    sdp_offer = message['sdpOffer']
    wrtc = media.WebRtcEndpoint(presenter['pipeline'])
    sessions[sessionId] = wrtc

    sdp_answer = wrtc.process_offer(sdp_offer)

    presenter['endpoint'].connect(wrtc)

    wrtc.gather_candidates()

    #logger.debug('SDP answer: ' + sdp_answer)
    emit('viewerResponse', {'id': 'presenterResponse', 'response': 'accepted', 'sdpAnswer': sdp_answer})


# mirror

def mirror_start(msg):
    sessionId = request.namespace.socket.sessid
    message = json.loads(msg)
    logger.debug('Connection ' + sessionId + ' received message ' + str(message))
    sdp_offer = message['sdpOffer']
    pipeline = kurento.create_pipeline()
    wrtc = media.WebRtcEndpoint(pipeline)
    sessions[sessionId] = wrtc

    wrtc.connect(wrtc)
    wrtc.on_media_session_started_event(on_event)
    wrtc.on_media_session_terminated_event(on_event)

    sdp_answer = wrtc.process_offer(sdp_offer)

    wrtc.gather_candidates()

    #logger.debug('SDP answer: ' + sdp_answer)
    emit('startResponse', {'id': 'startResponse', 'sdpAnswer': sdp_answer})


def webrtc_ice_candidate(msg):
    sessionId = request.namespace.socket.sessid
    message = json.loads(msg)
    logger.debug('Connection ' + sessionId + ' received message ' + str(message))
    logger.debug(sessions)

    wrtc = sessions[sessionId]

    wrtc.add_ice_candidate(message['candidate'])
