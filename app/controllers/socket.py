from flask_socketio import emit
from app import socketio

@socketio.on('connect')
def handle_connect():
    print("Usuario conectado al chat WebRTC")

@socketio.on('disconnect')
def handle_disconnect():
    print("Usuario desconectado")

# Mensajes de Chat de texto
@socketio.on('chat_message')
def handle_chat_message(data):
    emit('chat_message', data, broadcast=True)

@socketio.on('chat_reaction')
def handle_chat_reaction(data):
    # data: { msgId: ..., reaction: '😂', count: 1 } or similar.
    # We just distribute it to clients to increment that exact reaction.
    emit('chat_reaction', data, broadcast=True)

# Señalización de WebRTC (Peer-to-Peer)
@socketio.on('offer')
def handle_offer(data):
    # Se envía la oferta al otro peer
    emit('offer', data, broadcast=True, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, broadcast=True, include_self=False)

@socketio.on('ice_candidate')
def handle_ice(data):
    emit('ice_candidate', data, broadcast=True, include_self=False)
