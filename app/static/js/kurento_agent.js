
/*
 * Copyright 2016 The COMPEIT Consortium
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
kurentoAgent = function() {
    var participants = {};

    var server_cb = null;
    var room_cb = null;
    var user_cb = null;

    var local_media_cb = null;
    var remote_media_offer_cb = null;
    var remote_media_audio_change_cb = null;
    var remote_media_video_change_cb = null;
    var remote_sender_stopped_cb = null;

    var my_webRtcPeer = null;
    var my_video = null;

    var my_conn = null;


    function Participant(user_id, rVid) {
        this.uid = user_id;
        this.video = rVid;
        this.webRtcPeer = null;

        this.offerToReceiveVideo = function(wp, offerSdp){
            console.log('Invoking SDP offer callback function '+ this.uid);
            console.log('offerSdp ' + JSON.stringify(offerSdp));
            my_conn.sendServerMessage({'event': 'receive_start', 'offerSdp': offerSdp, 'sender':this.uid });
        };

        this.onIceCandidate = function(candidate) {
            console.log('Receiver candidate: ' + JSON.stringify(candidate))
            my_conn.sendServerMessage({'event': 'on_ice_candidate', 'candidate': candidate, 'sender':this.uid });
        };

        Object.defineProperty(this, 'webRtcPeer', { writable: true});
        Object.defineProperty(this, 'video', { writable: true});

        this.stop = function() {
            my_conn.sendServerMessage({'event': 'receive_stop'});
        };

        this.dispose = function() {
            console.log('Disposing participant ' + this.uid);
            this.webRtcPeer.dispose();
            //hideSpinner(this.video);
        };

        this.getVideo = function() {
            return this.video;
        }
    }

    function onError(error) {
        return console.error(error);
    }

    function user_msg(user_id, msg) {
        console.log('user: ' + user_id + ' msg: '+JSON.stringify(msg));

        if ('event' in msg) {
            switch (msg['event']) {
                case 'mediaOffer':
                    if (remote_media_offer_cb) {
                        if ('width' in msg && 'height' in msg) {
                            remote_media_offer_cb(user_id, msg['width'], msg['height']);
                        } else {
                            remote_media_offer_cb(user_id, undefined, undefined);
                        }
                    }
                    break;
            }
        }
    }

    function room_msg(user, msg) {
        console.log('msg('+user.id+'): '+JSON.stringify(msg));

        if (msg && 'event' in msg) {
            switch (msg['event']) {
                case 'mute':
                    if (remote_media_audio_change_cb) {
                        remote_media_audio_change_cb(user.id, 'muted');
                    }
                    break;
                case 'unmute':
                    if (remote_media_audio_change_cb) {
                        remote_media_audio_change_cb(user.id, 'unmuted');
                    }
                    break;
            }
        }
    }

    function server_msg(evt, msg) {
        console.log('event: ' + evt + ' msg: '+JSON.stringify(msg));
        switch (evt) {
            case 'send_started':
                my_webRtcPeer.processAnswer(msg['sdp_answer']);
                break;
            case 'send_started':
                break;
            case 'on_ice_candidate':
                //console.log('server candidate ');
                if ('sender' in msg) {
                    participant = participants[msg['sender']];
                    participant.webRtcPeer.addIceCandidate(msg['candidate']);
                } else {
                    my_webRtcPeer.addIceCandidate(msg['candidate']);
                }
                break;
            case 'receive_started':
                console.log('receive_started: '+msg['sender']);
                participant = participants[msg['sender']];
                participant.webRtcPeer.processAnswer(msg['sdp_answer']);
                break;
            case 'receive_stopped':
                break;
            case 'sender_stopped':
                var user_id = msg['sender'];
                if (remote_sender_stopped_cb) {
                    remote_sender_stopped_cb(user_id);
                }
                if (user_id in participants) {
                    my_webRtcPeer.dispose();
                    my_webRtcPeer = null;

                    participants[user_id].dispose();
                    delete participants[user_id];
                }
                break;
        }
    }

    function onIceCandidate(candidate) {
        console.log('Sender candidate ' + JSON.stringify(candidate));
        my_conn.sendServerMessage({'event': 'on_ice_candidate', 'candidate': candidate });
    }

    function onLocalOffer(error, offerSdp) {
        if (error) return onError(error);
        console.log('offerSdp ' + JSON.stringify(offerSdp));
        my_conn.sendServerMessage({'event': 'send_start', 'offerSdp': offerSdp });
    }

    function onLoadedMetadata() {
        var width = my_video.videoWidth;
        var height = my_video.videoHeight;

        console.log('w+h: '+width+'x'+height);
        if (local_media_cb) {
            local_media_cb(width, height);
        }
    }


    function create_constraints(minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate) {
        var mediaConstraints = {
            audio: true,
            video: {
                mandatory : {
                    maxWidth : 320,
                    maxHeight: 200,
                    maxFrameRate : 30,
                    minFrameRate : 30
                }
            }
        };

        if (minwidth != undefined) {
            mediaConstraints['video']['mandatory']['minWidth'] = minwidth;
            mediaConstraints['video']['mandatory']['maxWidth'] = minwidth;
        }

        if (maxwidth != undefined) {
            mediaConstraints['video']['mandatory']['maxWidth'] = maxwidth;
        }

        if (minheight != undefined) {
            mediaConstraints['video']['mandatory']['minHeight'] = minheight;
            mediaConstraints['video']['mandatory']['maxHeight'] = minheight;
        }

        if (maxheight != undefined) {
            mediaConstraints['video']['mandatory']['maxHeight'] = maxheight;
        }

        if (maxframerate != undefined) {
            mediaConstraints['video']['mandatory']['minFrameRate'] = minframerate;
            mediaConstraints['video']['mandatory']['maxFrameRate'] = minframerate;
        }

        if (maxframerate != undefined) {
            mediaConstraints['video']['mandatory']['maxFrameRate'] = maxframerate;
        }

        return mediaConstraints;
    }

    return {
        init: function(connectionAgent) {
            my_conn = connectionAgent.registerType('kurento', server_msg.bind(this), room_msg.bind(this), user_msg.bind(this));
        },

        startLocal: function(myVideo, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate) {
            if (!my_webRtcPeer) {
                if (myVideo != undefined) {
                    my_video = myVideo;
                }

                my_video.onloadedmetadata = onLoadedMetadata.bind(this);
                //showSpinner(my_video);

                var mediaConstraints = create_constraints(minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate);

                var options = {
                    mediaConstraints: mediaConstraints,
                    localVideo: my_video,
                    onicecandidate : onIceCandidate.bind(this)
                };

                my_webRtcPeer = kurentoUtils.WebRtcPeer.WebRtcPeerSendonly(options, function(error) {
                    if(error) return onError(error);
                    this.generateOffer(onLocalOffer);
                });

                var peer = my_webRtcPeer.peerConnection;
                peer.oniceconnectionstatechange = function() {
                    console.log('ice connection state changed: '+ peer.iceConnectionState);
                };
            }
        },

        changeLocal: function(minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate) {
            stopLocal();
            startLocal(undefined, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate);
        },

        muteAudioLocal: function() {
            var streams = my_webRtcPeer.peerConnection.getLocalStreams();
            if (!streams.length)
                return;
            for (var i = 0, stream; stream = streams[i]; i++) {
                var audioTracks = stream.getAudioTracks();

                // if MediaStream has reference to microphone
                if (audioTracks[0]) {
                    audioTracks[0].enabled = false;
                }
            }
            my_conn.sendRoomMessage({'event': 'mute'});
        },

        unmuteAudioLocal: function() {
            var streams = my_webRtcPeer.peerConnection.getLocalStreams();
            if (!streams.length)
                return;
            for (var i = 0, stream; stream = streams[i]; i++) {
                var audioTracks = stream.getAudioTracks();

                // if MediaStream has reference to microphone
                if (audioTracks[0]) {
                    audioTracks[0].enabled = true;
                }
            }
            my_conn.sendRoomMessage({'event': 'unmute'});
        },

        stopLocal: function() {
            my_conn.sendServerMessage({'event': 'send_stop'});
            my_webRtcPeer.dispose();
            my_webRtcPeer = null;
        },

        connectRemote: function(remoteVideo, user_id, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate) {
            if (user_id in participants) {
                participants[user_id].dispose();
                delete participants[user_id];
            }

            //showSpinner(rVid);

            var participant = new Participant(user_id, remoteVideo);
            participants[user_id] = participant;

            var mediaConstraints = create_constraints(minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate);


            var options = {
                mediaConstraints: mediaConstraints,
                remoteVideo: remoteVideo,
                onicecandidate : participant.onIceCandidate.bind(participant)
            }

            participant.webRtcPeer = kurentoUtils.WebRtcPeer.WebRtcPeerRecvonly(options, function(error) {
                if(error) return onError(error);
                this.generateOffer(participant.offerToReceiveVideo.bind(participant));
            });
        },

        changeRemote: function(user_id, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate) {
            if (user_id in participants) {
                var video = participants[user_id].video;
                stopRemote(user_id);
                connectRemote(video, user_id, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate);
            }
        },

        stopRemote: function(user_id) {
            if (user_id in participants) {
                my_conn.sendServerMessage({'event': 'send_stop'});
                my_webRtcPeer.dispose();
                my_webRtcPeer = null;

                participants[user_id].dispose();
                delete participants[user_id];
            }
        },

        offerUserMedia: function(user_id) {
            if (my_video.videoWidth && my_video.videoHeight) {
                my_conn.sendUserMessage(user_id, {'event': 'mediaOffer', 'width': my_video.videoWidth, 'height': my_video.videoHeight});
            } else {
                my_conn.sendUserMessage(user_id, {'event': 'mediaOffer'});
            }
        },

        onLocalMedia: function(cb) {
            local_media_cb = cb;
        },

        onRemoteMediaOffer: function(cb) {
            remote_media_offer_cb = cb;
        },

        onRemoteMediaVideoChange: function(cb) {
            remote_media_video_change_cb = cb;
        },

        onRemoteMediaAudioChange: function(cb) {
            remote_media_audio_change_cb = cb;
        },

        onRemoteSenderStopped: function(cb) {
            remote_sender_stopped_cb = cb;
        }
    }
}();
