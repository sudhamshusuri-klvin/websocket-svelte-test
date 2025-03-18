from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected clients
clients = 0

@app.route('/')
def index():
    return {"status": "Flask WebSocket Server Running"}

@socketio.on('connect')
def handle_connect():
    global clients
    clients += 1
    print(f'Client connected. Total clients: {clients}')
    emit('server_message', {'message': f'Welcome! You are client #{clients}'})
    # Broadcast to all clients that a new user has connected
    emit('server_message', {'message': f'A new client has connected. Total clients: {clients}'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global clients
    clients -= 1
    print(f'Client disconnected. Total clients: {clients}')
    emit('server_message', {'message': f'A client has disconnected. Total clients: {clients}'}, broadcast=True)

@socketio.on('client_message')
def handle_message(data):
    print(f'Received message: {data}')
    # Echo the message back with a timestamp
    emit('server_message', {
        'message': data['message'],
        'timestamp': time.time(),
        'echo': True
    })
    # Also broadcast to all other clients
    emit('server_message', {
        'message': f"Message from another client: {data['message']}",
        'timestamp': time.time(),
        'echo': False
    }, broadcast=True, include_self=False)

# Periodic random data emission (simulates server-initiated updates)
def background_task():
    """Example background task that sends periodic updates."""
    while True:
        socketio.sleep(1)
        if clients > 0:  # Only send if there are connected clients
            random_value = random.randint(1, 100)
            print(f"Emitting random update: {random_value}")
            socketio.emit('server_update', {
                'value': random_value,
                'timestamp': time.time()
            })

if __name__ == '__main__':
    socketio.start_background_task(background_task)
    socketio.run(app, debug=True, port=5000)
