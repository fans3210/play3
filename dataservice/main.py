import eventlet

from app.app import app, socketio, cworker

eventlet.monkey_patch()


if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True, host='0.0.0.0')
