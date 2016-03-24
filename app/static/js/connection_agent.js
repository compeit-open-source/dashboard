
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
 
connectionAgent = function() {
  var socket = null;
  var eventCBs = [];
  var roomCBs = [];
  var userCBs = [];
  var roomId = 0;
  var me = null;
  var evtCB = null;


  function eventCB(evt, data) {
    for (var type in eventCBs) {
      eventCBs[type](evt, data);
    }
    if (evtCB) {
      evtCB(evt, data);
    }
  }

  function logTypes() {
    for (var t in eventCBs) {
      console.log(t);
    }
  }


  return {
    init: function(room) {
      roomId = room;
    },
    start: function() {
      var namespace = '/connection_agent'; // change to an empty string to use the global namespace

      // the socket.io documentation recommends sending an explicit package upon connection
      // this is specially important when using the global namespace
      //var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
      socket = io.connect(document.domain + ':' + location.port + namespace);

      socket.on('connect', function() {
        console.log('Connection established');
      });

      socket.on('connected', function(msg) {
        console.log('Connected to connection agent');
        me = msg['user'];
        eventCB.call(this, 'connected', msg['user']);
        socket.emit('join_room', {'room': roomId});
      });


      socket.on('room_joined', function(msg) {
        //console.log('room_joined');
        eventCB.call(this, 'room_joined', {})
      });

      socket.on('user_joined', function(msg) {
        console.log('user_joined');
        //console.log(msg);
        if (me['id'] != msg['user']['id']) {
          eventCB.call(this, 'user_joined', msg);
        }
      });

      socket.on('user_left', function(msg) {
        console.log('user_left');
        console.log(msg);
        if (me['id'] != msg['user']['id']) {
          eventCB.call(this, 'user_left', msg);
        }
      });

      socket.on('server_message', function(msg) {
        if ('type' in msg && msg['type'] in eventCBs) {
          if ('data' in msg) {
            eventCBs[msg['type']](msg['event'], msg['data']);
          } else {
            eventCBs[msg['type']](null, msg['data']);
          }
        }
      });

      socket.on('room_message', function(msg) {
        // console.log('room_message received');
        // console.log(msg);
        if ('type' in msg && msg['type'] in roomCBs) {
          if ('data' in msg) {
            roomCBs[msg['type']](msg['user'], msg['data']);
          } else {
            roomCBs[msg['type']](msg['user']);
          }
        }
      });

      socket.on('user_message', function(msg) {
        // console.log('user_message received');
        // console.log(msg);
        if ('type' in msg && msg['type'] in userCBs) {
          if ('data' in msg) {
            userCBs[msg['type']](msg['from'], msg['data']);
          } else {
            userCBs[msg['type']](msg['from']);
          }
        }
      });

    },
    stop: function() {
      socket.close();
      eventCB('stopped', {});
      socket = null;
    },
    registerType: function(type, callbackEvent, callbackRoom, callbackUser) {
      var myType = type;
      if (callbackEvent) {
        eventCBs[type] = callbackEvent;
      }
      if (callbackRoom) {
        roomCBs[type] = callbackRoom;
      }
      if (callbackUser) {
        userCBs[type] = callbackUser;
      }

      return {
        sendServerMessage: function (msg) {
          this.sendServerMessage(myType, msg);
        }.bind(this),
        sendRoomMessage: function (msg) {
          this.sendRoomMessage(myType, msg);
        }.bind(this),
        sendUserMessage: function(user_id, msg) {
          this.sendUserMessage(user_id, myType, msg);
        }.bind(this),
        getType: function() {
          return myType;
        }.bind(this),
        debug: function() {
          this.debug();
        }.bind(this)
      }
    },
    getName: function () {
      return me.name;
    },
    onEvent: function (cb) {
      evtCB = cb;
    },
    sendServerMessage: function(type, msg) {
      socket.emit('server_message', {'type': type, 'data': msg});
    },
    sendRoomMessage: function(type, msg) {
      socket.emit('room_message', {'room': roomId , 'type': type, 'data': msg});
    },
    sendUserMessage: function(user_id, type, msg) {
      // console.log('user_message sent '+user_id+' '+type+' '+JSON.stringify(msg));
      socket.emit('user_message', {'to': user_id, 'type': type, 'data': msg});
    },
    debug: function() {
      logTypes();
    }
  }
}();
