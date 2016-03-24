
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
 
  var socket = null;
  var my_video;
  var my_webRtcPeer;
  var my_sdp;
  var my_state;
  var my_candidates = [];

  var participants = {};

  function Participant(user_id, rVid) {
    this.uid = user_id;
    this.video = rVid;
    var webRtcPeer;

    this.offerToReceiveVideo = function(wp, offerSdp){
      console.log('Invoking SDP offer callback function');
      console.log('offerSdp ' + JSON.stringify(offerSdp));
      socket.emit('receive_start', { sdpOffer: offerSdp, sender: this.uid });
    };

    this.onIceCandidate = function(candidate) {
      console.log('Receiver candidate: ' + JSON.stringify(candidate))
      socket.emit('on_ice_candidate', { candidate: candidate, sender: this.uid });
    };

    Object.defineProperty(this, 'webRtcPeer', { writable: true});
    Object.defineProperty(this, 'video', { writable: true});

    this.stop = function() {
      socket.emit('receive_stop', { sender: this.uid });
    };

    this.dispose = function() {
      console.log('Disposing participant ' + this.uid);
      this.webRtcPeer.dispose();
      hideSpinner(this.video);
    };
  }

  function onError(error) {
    return console.error(error);
  }

  function onIceCandidate(candidate) {
    console.log('Sender candidate ' + JSON.stringify(candidate));

    socket.emit('on_ice_candidate', { candidate: candidate });
  }

  function onOfferSend(error, offerSdp) {
    if (error) return onError(error);

    console.log('offerSdp ' + JSON.stringify(offerSdp));

    socket.emit('send_start', { sdpOffer: offerSdp });
  }

//
//{
//            mandatory: {
//                maxWidth: 640,
//                maxFrameRate: 15,
//                minFrameRate: 15
//            }
//        }


  function localVideo(constraints) {
    if (!my_webRtcPeer) {
      showSpinner(my_video);

      var mediaConstraints = {
        audio: true,
        video: {
          mandatory : {
              maxWidth : 100,
              maxHeight: 100,
              maxFrameRate : 30,
              minFrameRate : 30
          }
        }
      };

      var options = {
        mediaConstraints: mediaConstraints,
        localVideo: my_video,
        onicecandidate : onIceCandidate
      };

      my_webRtcPeer = kurentoUtils.WebRtcPeer.WebRtcPeerSendonly(options, function(error) {
        if(error) return onError(error);
        this.generateOffer(onOfferSend);
      });
    }
  }

  function remoteVideo(rVid, user_id) {
    if (user_id in participants) {
      participants[user_id].dispose();
      delete participants[user_id];
    }

    showSpinner(rVid);

    var participant = new Participant(user_id, rVid);
    participants[user_id] = participant;

    var mediaConstraints = {
      audio: true,
      video: {
        mandatory : {
            maxWidth : 640,
            maxHeight: 320,
            maxFrameRate : 30,
            minFrameRate : 30
        }
      }
    };

    var options = {
      mediaConstraints: mediaConstraints,
      remoteVideo: rVid,
      onicecandidate : participant.onIceCandidate.bind(participant)
    }

    participant.webRtcPeer = kurentoUtils.WebRtcPeer.WebRtcPeerRecvonly(options, function(error) {
      if(error) return onError(error);
      this.generateOffer(participant.offerToReceiveVideo.bind(participant));
    });
  }

  function hideSpinner() {
    for (var i = 0; i < arguments.length; i++) {
      arguments[i].src = '';
      arguments[i].poster = '/static/img/webrtc.png';
      arguments[i].style.background = '';
    }
  }

  function showSpinner() {
    for (var i = 0; i < arguments.length; i++) {
      arguments[i].poster = '/static/img/transparent-1px.png';
      arguments[i].style.background = 'center transparent url("/static/img/spinner.gif") no-repeat';
    }
  }

  $(document).ready(function(){
    console = new Console();
    console.log('lets go!');

    namespace = '/connection_agent'; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    //var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket = io.connect(document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
      console.log('Connected to connection agent');

    });

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('connected', function(msg) {
      console.log('connected');
      console.log(msg);

      $('#users').append('<div id="my_id" class="col-md-3 pull-left"  style="display:none"><div class="row">{{ current_user.name }}</div><div class="videoMini"><video id="my_video" autoplay height="125" width="164" poster="/static/img/webrtc.png"></video></div><button id="send">Send</button><button id="stop">Stop</button></div>');
      $('#my_id').fadeIn();

      my_video = document.getElementById('my_video');
      $('#send').click(function(event) {
        localVideo();
      });
      $('#stop').click(function(event) {
        socket.emit('send_stop');
      });

      window.onbeforeunload = function() {
        socket.close();
      };

      console.log('Joining room ' + {{ room.id }});
      socket.emit('join_room', {room: {{ room.id }} });
    });

    socket.on('room_message', function(msg) {
      console.log('room_message');
      console.log(msg);
      if ('user_id' in msg) {
        $('#user_chat_'+msg.user_id).append('<-'+msg.data+'\n');
      } else {
        var msgtext = '['+msg.user.name+']: '+msg.data+'\n';
        $('#room_chat_window').append(msgtext);
      }
    });

    socket.on('room_joined', function(msg) {
      console.log('room_joined');
      var msgtext = 'Entered the room\n';
      $('#room_chat_window').append(msgtext);
    });

    socket.on('send_started', function(message) {
      console.log('send_started');
      console.log(message);
      my_webRtcPeer.processAnswer(message.sdp_answer);
    });

    socket.on('send_stopped', function(message) {
      my_webRtcPeer.dispose();
      hideSpinner(my_video);
      my_webRtcPeer = null;
    });

    socket.on('av_available', function(message) {
      console.log('av_available')
      console.log(message);
      sender_id = message['sender'];
      if (sender_id == {{ current_user.id }}) {
        console.log('my av started');
        return;
      }
      rvid = document.getElementById('video_'+sender_id);
      remoteVideo(rvid, sender_id);
    });

    socket.on('av_not_available', function(message) {
      console.log('av_not_available')
      console.log(message);
      sender_id = message['sender'];
      if (sender_id == {{ current_user.id }}) {
        console.log('my av stopped');
        return;
      }
      participant = participants[sender_id];
      participant.stop();
    });


    socket.on('receive_started', function(message) {
      console.log('receive_started: '+message['sender']);
      participant = participants[message['sender']];
      participant.webRtcPeer.processAnswer(message.sdp_answer);
    });

    socket.on('receive_stopped', function(message) {
      console.log('receive_stopped')
      console.log(message);
      sender_id = message['sender'];
      participant = participants[sender_id];
      participant.dispose();
      delete participants[sender_id];
    });

    socket.on('user_joined', function(msg) {
      console.log('got user_add:');
      console.log(msg);
      var user = msg.user
      var msgtext = user.name+' is present in the room\n';
      $('#room_chat_window').append(msgtext);

      $('#users').append('<div id="user_'+user.id+'" class="col-md-3 pull-left"  style="display:none"><div class="row">'+user.name+'</div><div class="videoMini"><video id="video_'+user.id+'" height="125" width="164" autoplay poster="/static/img/webrtc.png"></video></div><div id="control_' + user.id + '""></div><div class="row">User chat window</div><div class="row"><textarea id="user_chat_'+user.id+'" class="form-control"  style="font-size:85%;" cols="80" rows="10" readonly="1"></textarea></div><div class="row"><input id="user_chat_input_'+user.id+'" user_id="'+user.id+'" type="textarea" class="form-control" placeholder="Message"></div></div></div>');

      $('#user_chat_input_'+user.id).keyup(function(event) {
        if (event.keyCode == 13) {
          socket.emit('user_message', {'data': $(this).val(), 'user_id':$(this).attr('user_id')});
          $('#user_chat_'+$(this).attr('user_id')).append('->'+$(this).val()+'\n')
          $(this).val('');
        }
      });

      $('#control_'+user.id).html('<button id="receive_'+user.id+'" user_id="'+user.id+'">Receive</button>');

      $('#receive_'+user.id).click(function(event) {
        console.log('receive video uid:'+$(this).attr('user_id'));
      });

      $('#user_'+user.id).fadeIn();
    });

    socket.on('user_left', function(msg) {
      console.log('got user_remove')
      console.log(msg);
      var user = msg.user
      var msgtext = user.name+' left the room\n';
      $('#room_chat_window').append(msgtext);

      $('#user_'+user.id).fadeOut(function() {
        $(this).remove();
      });
    });

    socket.on('room_left', function(msg) {
      window.location.href = "/";
    });

    $('#room_chat').keyup(function(event) {
      if (event.keyCode == 13) {
        console.log('return pressed')
        socket.emit('user_message', {room: {{ room.id }} , 'data': $('#room_chat').val()});
        $('#room_chat').val('');
      }
    });
  });
