import os
import requests

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
socketio = SocketIO(app)

all_chatrooms = list()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chatrooms")
def chatrooms():
    return render_template("chatrooms.html")


@socketio.on("create room")
def all_channels(data):

    room_taken = False

    if len(all_chatrooms) != 0:
        for room in all_chatrooms:
            if room["chat_title"] == data["chat_title"]:
                room_taken = True
                emit('room already exists')

    
    if room_taken != True:
        all_chatrooms.append(data)
        emit('room created',  data, broadcast =True)



@socketio.on("connect")
def load():
    emit('all chatrooms loaded', {'data': all_chatrooms}, broadcast=False)
    


@app.route("/channel/<string:room>")
def channel(room):

    for item in all_chatrooms:      
        if int(item['id']) == int(room):
            return render_template("channel.html", name=item['chat_title'])
  
    return ''


@socketio.on("user joined channel")
def current_channel(data):
    room = data['room_id']
    username = data['username']
    join_room(room)

    print(f'New user {username} joined room {room} ')
    emit('user has joined the room', room=room)



@socketio.on("message sent")
def message(data):
    room = data['room_id']

    if len(all_chatrooms) != 0:
        for item in all_chatrooms:
            if item["id"] == data["room_id"]:
                item["all_messages"].append(data['message'])

    emit('message processed', data, room=room)


@socketio.on("leave room")
def leave(data):
    room = data['room_id']
    username = data['username']
    leave_room(room)
    emit('user left')