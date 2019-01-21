import socketio
import tornado

# create a Socket.IO server
sio = socketio.AsyncServer(async_mode='tornado')

# wrap with ASGI application
app = tornado.web.Application(
    [
        (r"/socketio.io/", socketio.get_tornado_handler(sio)),
    ],
    # ... other application options
)

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

app.listen(5000)
tornado.ioloop.IOLoop.current().start()