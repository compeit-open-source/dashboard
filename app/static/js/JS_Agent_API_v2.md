# COMPEIT Server JS Agent API v2.0

## Connection Agent

Connection Agent is responsible for communication with the COMPEIT server and the participants in a room. All clients connect to the Connection Agent when they want to join a room. It is implemented in the server as `connection_agent.py`and in the clients as `connection_agent.js`. Connection Agent provides an interface where other modules can register themselves by using a unique agent `type`. The registered agent can then communicate with the server, the other clients within a room, or a specific client by the use of returned methods and registered callbacks. Connection Agent uses `socket.io` version -0.04 as the base for communication with the namespace `/connection_agent`.

### JS API 

The Connection Agent API is implemented as the `connectionAgent` object in `connection_agent.js` and provides the following methods:
* `init(roomId)` initializes the object for the given room
* `start()` starts connecting to the server and joins the room
* `stop()` leaves the room and disconnects from the server
* `register_type(type, callbackEvent, callbackRoom, callbackUser)`
  - returns an object which should be used for communication for that agent type. The objects implements the following methods:
    * `sendServerMessage(msg)` sends a message of the registered `type` to the server
    * `sendRoomMessage(msg)` sends the message to all participants the connected room
    * `sendUserMessage(userId, msg)` sends the message to the given user
  - and the corresponding callback for the `type` are:
    * `callbackEvent(event, data)` - a server event
    * `callbackRoom(<user>, data)` - a message to the room from `<user>` 
    * `callbackUser(<user>, data)` - a message to the client from `<user>`
* `onEvent(callback)` - register for callbacks on events
  - `callback(event, msg)` - where the events are:
  	* `connected` - `msg` is the `<user>` connected
  	* `room_joined` - `msg` is empty
  	* `room_left` - `msg` is empty
  	* `user_joined` - `msg` is the `<user>` that joined
  	* `user_left` - `msg` is the `<user>` that left

### Example Signalling diagram

## Kurento Agent

Kurento Agent is an example agent providing WebRTC communication and it uses the `kurento` type. The agent provides methods for sending, offering, and receiving WebRTC streams, and additional methods for manipulating said streams. It is implemented in the server as `kurento_agent.py` and in the clients as `kurento_agent.js`.

### JS API

* `init(connectionAgent)` initializes the object for the given Connection Agent
* `startLocal(myVideo, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate)` starts sending a WebRTC stream to the kurento server using the HTML5 video object `myVideo` and with the given properties (the video properties are optional).
* `muteAudioLocal()` disables the audio stream
* `unmuteAudioLocalfunction()` enables the audio stream
* `stopLocal()` stop sending the WebRTC stream
* `connectRemote(remoteVideo, user_id, minwidth, minheight, minframerate, maxwidth, maxheight, maxframerate)` starts receiving a WebRTC stream from the user identifier `user_id` available on the kurento server using the HTML5 video object `remoteVideo` and with the given properties (the video properties are optional).
* `stopRemote(user_id)` stop receiving the WebRTC stream from user `user_id`
* `offerUserMedia(user_id)` offer WebRTC media stream to the user `user_id`
* `onLocalMedia(callback)` callback triggered when media is sent to the Kurento server
  - `callback(width, height)` - video properties `width` and `height`
* `onRemoteMediaOffer(callback)` callback triggered when a remote user is offering a WebRTC media stream
  - `callback(user_id, width, height)` - `user_id` offers video with `width`, `height` properties
* `onRemoteMediaAudioChange(callback)` callback triggered when a remote stream changes audio properties
  - `callback(user_id, event)` - `user_id` is the remote user and `event` can be either `muted` or `unmuted`
* `onRemoteSenderStopped(callback)` callback triggered when a remote stream stopped sending
  - `callback(user_id)` - `user_id` stopped sending

### Example signalling diagram 

## Chat Agent

Chat Agent is an example agent providing chat communication and it uses the `chat` type. The agent provides methods for room chat, user to user chat and server events in the room chat. It is implemented in the server as `chat_agent.py` and in the clients as `chat_agent.js`.

### JS API

The Chat Agent API is implemented as the `chatAgent` object in `chat_agent.js` and provides the following methods
* `init(connectionAgent)` initializes the object for the given Connection Agent
* `roomMessage(msg)` sends the message to all participants the connected room
* `userMessage(userId, msg)` sends the message to the given user
* `onServerMessage(callback)` register callback for server messages and events
  - `callback(msg)` - `msg` is the server message
* `onRoomMessage(callback)` register callback for room messages
  - `callback(<user>, msg)` - `<user>` is the originating user and `msg` is the user message
* `onUserMessage(callback)` register callback for user messages
  - `callback(<user>, msg)` - `<user>` is the originating user and `msg` is the user message

### Example signalling diagram 

