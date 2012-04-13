import imp
zmq = None
def _use_gevent():
    global zmq
    f, p, d = imp.find_module('gevent_zeromq')
    mod = imp.load_module('gevent_zeromq', f, p, d)
    zmq = mod.zmq
def _use_zmq():
    global zmq
    f, p, d = imp.find_module('zmq')
    zmq = imp.load_module('zmq', f, p, d)

# Use the regular module by default
_use_zmq()

from lwr.plugins.zmq.message import MessageHandler
from lwr.planner.plan import Event
from lwr.events.interface import EventReceiver, EventPublisher

class ZMQEventReceiver(EventReceiver):
    def __init__(self, store=None):
        """
        If store is set it should be an EventStore object where we'll save
        events as they arrive
        """
        self.sockets = []
        self.poller = zmq.core.poll.Poller()
        self.mh = MessageHandler()
        self.store = store

    def listen(self, sock):
        """
        Add sock (a zmq socket) to list of sockets we'll listen for events on
        """
        self.sockets.append(sock)
        self.poller.register(sock, zmq.POLLIN)

    def getEvent(self, timeout=None):
        """
        Get the next event. Wait for timeout milli-seconds or forever if timeout is
        None
        """
        socks = self.poller.poll(timeout)
        if not socks:
            return
        msg = socks[0][0].recv()
        d = self.mh.unserialize(msg)
        e = Event.fromDict(d)
        if self.store:
            _id = self.store.addEvent(e)
            e.id = _id
        return e

class ZMQEventPublisher(EventPublisher):
    def __init__(self):
        self.sockets = []
        self.mh = MessageHandler()

    def addSocket(self, sock):
        self.sockets.append(sock)

    def sendEvent(self, e):
        msg = self.mh.serialize(e.asDict())
        for sock in self.sockets:
            sock.send(msg)

if __name__ == '__main__':
    ctx = zmq.core.Context()

    sock = ctx.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, '')
    sock.connect("tcp://localhost:5556")

    es = ZMQEventReceiver()
    es.listen(sock)

    pubsock = ctx.socket(zmq.PUB)
    pubsock.bind("tcp://0.0.0.0:5556")
    ep = ZMQEventPublisher()
    ep.addSocket(pubsock)

    e = Event(owner='me', bucket='public', name='hg.pushes', data={'branch': 'mozilla-central', 'rev': '1234567890'})
    import time
    time.sleep(0.5)
    ep.sendEvent(e)

    events = []

    while True:
        e_recv = es.getEvent(1000)
        print e_recv, id(e_recv), id(e)
        ep.sendEvent(e)
        time.sleep(0.5)
        events.append(e_recv)
