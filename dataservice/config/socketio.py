from flask_socketio import Namespace, emit, join_room
import app.app as app


class DataNamespace(Namespace):
    def on_connect(self):
        print('new client connected')

    def on_disconnect(self):
        print('client disconnected')

    def on_join(self, client_id):
        print('on join received, ', client_id)
        join_room(client_id)
        emit('joined room', {"room": client_id}, room=client_id)
        app.client_id = client_id
