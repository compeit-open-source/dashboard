
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
 
chatAgent = function () {
    var ca = null;
    var server_cb = null;
    var room_cb = null;
    var user_cb = null

    function user_chat_msg(user, msg) {
      if (user_cb) {
        user_cb(user, msg);
      }
    }

    function room_chat_msg(user, msg) {
      if (room_cb) {
        room_cb(user.name, msg);
      }
    }

    function server_msg(msg) {
      if (server_cb) {
        server_cb(msg);
      }
    }

    return {
      init: function(connectionAgent) {
        ca = connectionAgent.registerType('chat', server_msg, room_chat_msg, user_chat_msg);
      },
      onServerMessage: function(cb) {
        server_cb = cb;
      },
      onRoomMessage: function(cb) {
        room_cb = cb;
      },
      onUserMessage: function(cb) {
        console.log('defined')
        user_cb = cb;
      },
      roomMessage: function(msg) {
        ca.sendRoomMessage(msg);
      },
      userMessage: function(user_id, msg) {
        ca.sendUserMessage(user_id, msg);
      },
      debug: function() {
        ca.debug();
      }
    }
}();
