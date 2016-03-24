
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
 
simpleRoomAgent = function () {
    var ca = null;
    var conn = null;
    var chat = null;

    return {
      init: function(connectionAgent, chatAgent) {
        ca = connectionAgent;
        chat = chatAgent;
        conn = ca.registerType('simple_room', function (evt, msg) {
          switch (evt) {
          case 'connected':
            break;
          case 'room_joined':
            this.room_joined();
            break;
          case 'user_joined':
            this.user_joined(msg.user.id, msg.user.name)
            break;
          case 'user_left':
            this.user_left(msg.user.id)
            break;
          default:
            console.log('unhandled event: '+evt)
          }
        }.bind(this), null, null);

        chat.onServerMessage(function(msg) {
          var msgtext = 'Server says '+msg+'\n';
          $('#room_chat_window').append(msgtext);
        });
        chat.onRoomMessage(function(user_name, msg) {
          var msgtext = '['+user_name+']: '+msg+'\n';
          $('#room_chat_window').append(msgtext);
        });
      },

      ready: function() {
        $('#room_chat').keyup(function(event) {
          if (event.keyCode == 13) {
            chat.roomMessage($('#room_chat').val());
            $('#room_chat').val('');
          }
        }.bind(this));
      },

      room_joined: function () {
        $('#users').append('<div id="my_id" class="col-md-3 pull-left"  style="display:none"><div class="row">'+ca.getName()+'</div><div class="videoMini"><video id="my_video" autoplay height="125" width="164" poster="/static/img/webrtc.png"></video></div><button id="send">Send</button><button id="stop">Stop</button></div>');
        $('#my_id').fadeIn();
      },

      get_chat: function() {
        return chat;
      },

      user_joined: function(user_id, user_name) {
        var that = this;

        $('#users').append('<div id="user_'+user_id+'" class="col-md-3 pull-left"  style="display:none"><div class="row">'+user_name+'</div><div class="videoMini"><video id="video_'+user_id+'" height="125" width="164" autoplay poster="/static/img/webrtc.png"></video></div><div id="control_' + user_id + '""></div><div class="row">User chat window</div><div class="row"><textarea id="user_chat_'+user_id+'" class="form-control"  style="font-size:85%;" cols="80" rows="10" readonly="1"></textarea></div><div class="row"><input id="user_chat_input_'+user_id+'" user_id="'+user_id+'" type="textarea" class="form-control" placeholder="Message"></div></div></div>');

        $('#user_chat_input_'+user_id).keyup(function(event) {
          if (event.keyCode == 13) {
            console.log(event);
            console.log(that.get_chat());
            console.log(that.chat);
            //that.chat.userMessage($(this).attr('user_id'), $(this).val())
            //socket.emit('user_message', {'data': $(this).val(), 'user_id':$(this).attr('user_id')});
            $('#user_chat_'+$(this).attr('user_id')).append('->'+$(this).val()+'\n')
            $(this).val('');
          }
        });
        $('#user_'+user_id).fadeIn();
      },

      user_left: function (user_id) {
        $('#user_'+user_id).fadeOut(function() {
          $(this).remove();
        });
      },

      debug: function() {
        connection.debug();
      }
    }
}();
