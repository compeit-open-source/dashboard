
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

from flask import render_template, session, redirect, url_for, request, flash, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.socketio import emit, join_room, leave_room

from . import ws
from .. import socketio, db
from ..models import User, Chat


# WS Socket communication

ws_clients = {}

@socketio.on('connect', namespace='/dashboard_index')
@login_required
def dashboard_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('join_room', namespace='/dashboard_index')
def room_join(message):
    roomId = int(message['room'])
    print "got join_room for " + str(roomId)

    print request.namespace
    print request.namespace.socket.sessid

    ws_clients[current_user.username] = request.namespace

    if current_user.activeRoomId and int(current_user.activeRoomId) != int(roomId):
        print "leaving room " + str(current_user.activeRoomId) + " to room " + str(roomId)
        join_room(current_user.activeRoomId)
        leave_room(current_user.activeRoomId)

    join_room(roomId)
    if not current_user.activeRoomId or int(current_user.activeRoomId) != int(roomId):
        current_user.activeRoomId = roomId
        db.session.commit()


@socketio.on('leave_room', namespace='/dashboard_index')
def room_leave(message):
    if current_user.activeRoomId:
        leave_room(current_user.activeRoomId)

    current_user.activeRoomId = None
    db.session.commit()

    emit('left_room', {})


@socketio.on('disconnect', namespace='/dashboard_index')
@login_required
def dashboard_disconnect():
    current_user.activeRoomId = None
    db.session.commit()
    print('Client disconnected')


@socketio.on('user_message', namespace='/dashboard_index')
def user_message(message):
    print request.namespace
    print request.namespace.socket.sessid

    if current_user.activeRoomId:
        c = Chat(roomId=current_user.activeRoomId, userId=current_user.id, datetime=datetime.utcnow(), text=message['data']['text'])
        db.session.add(c)
        db.session.commit()
        #ws_clients[current_user.username].socketio.emit('room_message', {'data': 'Hello', 'user': 'Server'}, namespace=ws_clients[current_user.username].ns_name, room=int(current_user.activeRoomId))

        emit('room_message',
             {'data': message['data'], 'user': current_user.name},
             room=int(current_user.activeRoomId))

'''
@socketio.on('connect', namespace='/connection_agent')
def ca_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('invite', namespace='/connection_agent')
def ca_invite():
    join_room(roomId)
    emit('setOwnID', {"clientid": current_user.username });
    emit('setRoomClientsIDs', {"clientList": []}, room=roomId)


@socketio.on('message', namespace='/connection_agent')
def ca_message(message):
    emit('message', message, room=roomId)


@socketio.on('exit', namespace='/connection_agent')
def ca_exit():
    emit('bye', {'clientid': current_user.username}, room=current_user.activeRoomId)
    leave_room(current_user.activeRoomId)


@socketio.on('disconnect', namespace='/connection_agent')
def ca_disconnect():
    print('Client disconnected')
'''


'''
//////////////////////////////////
// Server Node.js with socket.IO //
///////////////////////////////////



/**
 * Declare the variable messages for the chat
 */
var messages = new Array();
var cards = new Array();
var bets = new Array();
var pots= new Array();
var stacks = new Array();
var players=  new Array();
var foldedPlayers = new Array();
var clientIDs = new Array();


/**
* When a user connects
*/
io.sockets.on('connection', function (client) {
    var PlayerID;
    var room;
    var myCards = new Array(52);


    client.on("invite", function(invitation){
        room = invitation;
        playerID = io.sockets.clients(room).length; //client.id;//Math.random();//io.sockets.clients(room).length;
        client.set('playerID', parseFloat(playerID));
        client.emit('assignPlayerID', {"playerID" : parseFloat(playerID)});
        if (io.sockets.clients(room).length < 1){ // ie you are the first in this room
            messages[room] = new Array();
            cards[room] = new Array(52);
            players[room] = new Array();
            bets[room] = new Array();
            stacks[room] = new Array();
            client.emit('setInitiator', {"initiator" : 0});
            }
        else{
            client.broadcast.to(room).emit('setInitiator', {"initiator" : 0});
            client.emit('setInitiator', {"initiator" : 1});
            };

        client.join(room);

        client.emit('setOwnID', {"clientid": client.id });
        client.set('piggybank', 1000.);
        client.emit('updateStack', 1000.);
        client.set('currentBet', 0.);
        client.emit('updateBet', 0.);

        var tmp= new Array();
        for(var i= 0.; i< io.sockets.clients(room).length; i++){
            if(io.sockets.clients(room)[i].id != client.id){
                tmp.push(io.sockets.clients(room)[i].id);};
            };

        client.emit('setRoomClientsIDs', {"clientList": tmp})
    });

    client.on('setNickName', function(nickname){
        bets[room]=[];
        stacks[room]=[];
        players[room] =[];
    //  client.set('playerID', nickname); temporarily disabled
        for(var i= 0.; i< io.sockets.clients(room).length; i++){
            io.sockets.clients(room)[i].get('playerID', function(err, value){ players[room].push(value)});
            io.sockets.clients(room)[i].get('currentBet', function(err, value){ bets[room].push(value)});
            io.sockets.clients(room)[i].get('piggybank', function(err, value){ stacks[room].push(value)});
            };
        io.sockets.in(room).emit('updateBets', {"names": players[room], "bets": bets[room], "stacks": stacks[room], "pot": pots[room]});
        });




    /**
     * When a user send a SDP message
     * broadcast to all users in the room
     */
    client.on('message', function(message) {
        var msg = JSON.parse(message);

       // client.broadcast.to(room).send(message);
       if(msg.ToID)
            io.sockets.socket(msg.ToID).send(message);

        else
            client.broadcast.to(room).send(message);

    });



    /**
     * When the user hang up
     * broadcast bye signal to all users in the room
     */
    client.on('exit',function(){
        client.broadcast.to(room).emit('bye', {"clientid": client.id});
    });

    /**
     * When the user close the application
     * broadcast close signal to all users in the room
     */
    client.on('disconnect',function(){
        client.broadcast.to(room).emit('bye', {"clientid": client.id});
        //remove yourself from client list
    });


    //// game stuff ///
    client.on('dealCards', function(){
        var i,f;

        pots[room] =0.;
        bets[room]=[];
        stacks[room]=[];
        players[room] =[];
        foldedPlayers[room]=0.;
        for ( i =0; i< 52;i++) cards[room][i]=i;
        shuffle (cards[room]);

        for( i= 0; i< io.sockets.clients(room).length; i++){
            for(j=0; j< 52; j++) myCards[j]=999;
            myCards[5 + 2*i] = cards[room][[5 + 2*i]];
            myCards[6 + 2*i] = cards[room][[6 + 2*i]];
            io.sockets.clients(room)[i].emit('dealCards', myCards );
            io.sockets.clients(room)[i].set('cardsFolded', 0);
            io.sockets.clients(room)[i].get('playerID', function(err, value){ players[room].push(value)});
            io.sockets.clients(room)[i].set('currentBet', 0);
            io.sockets.clients(room)[i].get('currentBet', function(err, value){ bets[room].push(value)});
            io.sockets.clients(room)[i].get('piggybank', function(err, value){ stacks[room].push(value)});
            };
        io.sockets.in(room).emit('updateBets', {"names": players[room], "bets": bets[room], "stacks": stacks[room], "pot": pots[room]});
        });

    client.on('dealFlop', function(){
        for( i= 0; i< io.sockets.clients(room).length; i++){
            for(j=0; j< 52; j++) myCards[j]=999;
            myCards[0] = cards[room][0];
            myCards[1] = cards[room][1];
            myCards[2] = cards[room][2];
            myCards[5 + 2*i] = cards[room][[5 + 2*i]];
            myCards[6 + 2*i] = cards[room][[6 + 2*i]];
            io.sockets.clients(room)[i].emit('dealFlop', myCards );
            };
        });

    client.on('dealTurn', function(){
        for( i= 0; i< io.sockets.clients(room).length; i++){
            for(j=0; j< 52; j++) myCards[j]=999;
            myCards[0] = cards[room][0];
            myCards[1] = cards[room][1];
            myCards[2] = cards[room][2];
            myCards[3] = cards[room][3];
            myCards[5 + 2*i] = cards[room][[5 + 2*i]];
            myCards[6 + 2*i] = cards[room][[6 + 2*i]];
            io.sockets.clients(room)[i].emit('dealTurn', myCards );
            };
        });

    client.on('dealRiver', function(){
        for( i= 0; i< io.sockets.clients(room).length; i++){
            for(j=0; j< 52; j++) myCards[j]=999;
            myCards[0] = cards[room][0];
            myCards[1] = cards[room][1];
            myCards[2] = cards[room][2];
            myCards[3] = cards[room][3];
            myCards[4] = cards[room][4];
            myCards[5 + 2*i] = cards[room][[5 + 2*i]];
            myCards[6 + 2*i] = cards[room][[6 + 2*i]];
            io.sockets.clients(room)[i].emit('dealRiver', myCards );
            };
        });

    client.on('showDown', function(){io.sockets.in(room).emit('showDown', cards[room]);
        });

    client.on('placeBet', function(bet){
        bets[room]=[];
        stacks[room]=[];
        players[room] =[];
        pots[room]+= parseFloat(bet);
        client.get('piggybank',function(err, value){client.set('piggybank', value - parseFloat(bet));});
        client.get('currentBet', function(err, value){client.set('currentBet', (value + parseFloat(bet)));});
        for(var i= 0.; i< io.sockets.clients(room).length; i++){
            io.sockets.clients(room)[i].get('playerID', function(err, value){ players[room].push(value)});
            io.sockets.clients(room)[i].get('currentBet', function(err, value){ bets[room].push(value)});
            io.sockets.clients(room)[i].get('piggybank', function(err, value){ stacks[room].push(value)});
            };
        io.sockets.in(room).emit('updateBets', {"names": players[room], "bets": bets[room], "stacks": stacks[room], "pot": pots[room]});
        });

    client.on('foldCards', function(){
        var  i;
        bets[room]=[];
        stacks[room]=[];
        players[room] =[];
        client.set('cardsFolded', 1.);
        foldedPlayers[room] = foldedPlayers[room] + 1.;

        console.log("folded players :  " + foldedPlayers[room] );
            console.log("n clients :  " + io.sockets.clients(room).length);
            console.log("pot1= " + pots[room]);

        if(foldedPlayers[room] > (io.sockets.clients(room).length - 2)) {
            for(i= 0; i< io.sockets.clients(room).length; i++){
                io.sockets.clients(room)[i].get('cardsFolded',function(err, value){
                    if(value!=1.) {io.sockets.clients(room)[i].get('piggybank',function(err, value2){io.sockets.clients(room)[i].set('piggybank', value2 + pots[room]);});
                                    console.log('not folded')}
                    else console.log('folded');
                    });
                io.sockets.clients(room)[i].set('cardsFolded', 0.);
                io.sockets.clients(room)[i].set('currentBet', 0.);
                io.sockets.clients(room)[i].get('playerID', function(err, value){ players[room].push(value)});
                io.sockets.clients(room)[i].get('currentBet', function(err, value){ bets[room].push(value)});
                io.sockets.clients(room)[i].get('piggybank', function(err, value){ stacks[room].push(value)});
                };
        //io.sockets.clients(room)[i].get('piggybank', function(err, value){console.log("pot now :"+ value) });

        pots[room]=0;
        io.sockets.in(room).emit('foldCards', {"names": players[room], "bets": bets[room], "stacks": stacks[room], "pot": pots[room]});
        foldedPlayers[room] =0;
        };
    });
###

});
'''
