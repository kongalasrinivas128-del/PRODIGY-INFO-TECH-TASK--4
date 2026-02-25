from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

users = {}
rooms = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username.strip():
            session['username'] = username
            users[username] = True
            return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@socketio.on('join')
def handle_join(data):
    try:
        room = data.get('room', '').strip()
        user = data.get('user', 'Unknown').strip()
        if room and user:
            join_room(room)
            if room not in rooms:
                rooms[room] = []
            rooms[room].append(user)
            timestamp = datetime.now().strftime('%H:%M:%S')
            # Emit to the room (server-side uses `room=`)
            emit('message', {'user': 'System', 'message': f"{user} joined the room.", 'timestamp': timestamp, 'type': 'join'}, room=room)
    except Exception as e:
        print(f"Error in join: {e}")

@socketio.on('send_message')
def handle_message(data):
    try:
        room = data.get('room', '').strip()
        message = data.get('message', '').strip()
        user = data.get('user', 'Unknown').strip()
        if room and message:
            timestamp = datetime.now().strftime('%H:%M:%S')
            emit('message', {'user': user, 'message': message, 'timestamp': timestamp, 'type': 'user'}, room=room)
    except Exception as e:
        print(f"Error in send_message: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
