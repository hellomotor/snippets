from sys import stderr
import socket
import select
import errno
from traceback import print_exc
from struct import unpack_from


class Reactor:
    HeaderStart = 0 
    BodyPart    = 1 
    BodyOK      = 2 
    StatusString = [ 'HeaderStart', 'BodyPart', 'BodyOK' ]

    def __init__(self, host, port, select_timeout=None):
        self._connected = False
        self._sock = None
        self._reqs_list = []
        self._status = Reactor.HeaderStart
        self._packet_len = 0
        self._buffer = []
        self._connect(host, port)
        self._select_timeout = select_timeout

    def _connect(self, host, port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        self._sock.setblocking(0)

    def _pump_event(self):
        r, w = [ self._sock ], []
        if self._reqs_list:
            w.append(self._sock)
        rfds, wfds, efds = select.select(r, w, [], self._select_timeout)
        [ self._handle_read(sock) for sock in rfds ]
        [ self._handle_write(sock) for sock in wfds ]
        if not (rfds or wfds or efds):
            self.on_idle()

    def on_close(self):
        pass

    def on_idle(self):
        pass

    def on_data(self, data):
        assert False, 'on_data not implemented'

    def on_test_srv(self, data):
        print 'testsrv recved: ', len(data)

    def _my_recv(self, sock, byte):
        data = sock.recv(byte)
        if not data:
            raise socket.error('remote end has close connection')
        return data

    def on_header_start(self, data):
        if len(data) < 8:
            self.on_test_srv(data)
            return
        (flag, self._packet_len) = unpack_from('<4si', data, 0)
        assert flag == '2003', 'invalid packet header'
        length = len(data) - 8
        if length < self._packet_len:
            self._buffer = list(data[8 : ])
            self._status = Reactor.BodyPart
        elif length == self._packet_len:
            self._buffer = list(data[8 : ])
            self.on_body_ok()
            self._status = Reactor.HeaderStart
        else:
            offset = self._packet_len + 8
            self._buffer = list(data[8 : offset])
            self.on_body_ok()
            self.on_header_start(data[offset : ])

    def on_body_part(self, data):
        assert len(self._buffer) > 0, 'buffer cannot be empty'
        left = self._packet_len - len(self._buffer)
        if len(data) < left:
            self._buffer.extend(data)
            self._status = Reactor.BodyPart
        elif len(data) == left:
            self._buffer.extend(data)
            self.on_body_ok()
            self._status = Reactor.HeaderStart
        else:
            self._buffer.extend(data[ : left])
            self.on_body_ok()
            self.on_header_start(data[left : ])

    def on_body_ok(self):
        assert len(self._buffer) == self._packet_len, 'incomplete network packet'
        self.on_data(''.join(self._buffer))
        self._packet_len = 0
        self._buffer = []

    def _do_recv(self, sock):
        buff  = []
        try:
            while True:
                buff.extend(self._my_recv(sock, 4096))
        except socket.error, er:
            if er.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                pass
            else:
                raise
        data = ''.join(buff)
        #print '%d bytes recv' % len(data)

        if self._status == Reactor.HeaderStart:
            self.on_header_start(data)
        elif self._status == Reactor.BodyPart:
            self.on_body_part(data)
        else:
            pass
            
    def _handle_read(self, sock):
        self._do_recv(sock)
        
    def _my_sendall(self, sock, msg):
        totalsent, msglen = 0, len(msg)
        try:
            while totalsent < msglen:
                sent = sock.send(msg[totalsent:])
                if sent == 0:
                    raise socket.error("socket connection broken")
                totalsent += sent
            return totalsent
        except socket.error, e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return totalsent
            else:
                raise

    def _handle_write(self, sock):
        while self._connect and self._reqs_list:
            buf = self._reqs_list.pop()
            sent = self._my_sendall(sock, buf)
            if sent < len(buf):
                self._reqs_list.append(buf[sent:])

    def on_connect_lost(self):
        pass

    def run(self):
        try:
            while self._sock:
                self._pump_event()
        except:
            print_exc(file=stderr)
            self.on_connect_lost()

    def close(self):
        try:
            if self._sock:
                self._sock.close()
                self._sock = None
            self._buffer = []
            self._packet_len = 0
            self._status = Reactor.HeaderStart
        except:
            pass
            #print 'close error, %s' % ex

    def send(self, req):
        self._reqs_list.append(req)
        self._pump_event()
