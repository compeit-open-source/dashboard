# COMPEIT Server WS API v2.0

## Connection Agent

Connection Agent is responsible for communication with the COMPEIT server and the participants in a room. All clients connect to the Connection Agent when they want to join a room. It is implemented in the server as `connection_agent.py`and in the clients as `connection_agent.js`. Connection Agent provides an interface where other modules can register themselves by using a unique agent `type`. The registered agent can then communicate with the server, the other clients within a room, or a specific client by the use of returned methods and registered callbacks. Connection Agent uses `socket.io` version 0.96 as the base for communication with the namespace `/connection_agent`.

### Messages and events

The base protocol is a basic protocol which registers events for connections, user joining and leaving a room, message destined to the server, room or a specific client. 

#### Message types (events):

* connection
  - client request: `connect`, no arguments.
  - server reply: `connected`, `{ user: <user> }` where the `<user>` connected is returned
* joining a room
  - client request: `join_room`, `{ room: <int: roomId> }` where `roomId` is the internal integer of the room.
  - server reply: `room_joined`
* leaving a room
  - client request: `leave_room`, no arguments
  - server reply: `room_left`
* send messages to the server
  - client: `server_message`, `{ type: <string: type>, data: <data> }` where `type` is the registered agent type, and `<data>` the argument
* send messages to the active roomn
  - client: `room_message`, `{ type: <string: type>, data: <data> }` where `type` is the registered agent type, and `<data>` the argument
* send messages to a specific user 
  - client: `server_message`, `{ to: <int: userId>, <type: <string: type>, data: <data> }` where `userId` is the generated id for the user, `type` is the registered module type, and `<data>` the argument

## Kurento Agent

Kurento Agent is an example agent providing WebRTC communication and it uses the `kurento` type. The agent provides methods for sending, offering, and receiving WebRTC streams, and additional methods for manipulating said streams. It is implemented in the server as `kurento_agent.py`and in the clients as `kurento_agent.js`.

### Messages and events

#### Message types (events):

## Chat Agent

Chat Agent is an example agent providing chat communication and it uses the `chat` type. The agent provides methods for room chat, user to user chat and server events in the room chat. It is implemented in the server as `chat_agent.py`and in the clients as `chat_agent.js`.

### Messages and events

#### Message types (events):

