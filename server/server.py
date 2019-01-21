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

app.listen(6000)
tornado.ioloop.IOLoop.current().start()