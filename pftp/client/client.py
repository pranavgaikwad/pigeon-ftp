import socket
from pftp.utils.logger import logger


class SendError(Exception):
    pass


class ReceiveError(Exception):
    pass


class UnsupportedSizeError(Exception):
    pass


class Client(object):
    """ A generic UDP client 
    
    Provides udt_send and udt_recv to send data on an un-reliable channel.
    """

    # MSS value cannot be higher than this
    RECV_BUF_SIZE = 65535
    SEND_BUF_SIZE = 4096

    # this is not the ARQ timeout
    # internal timeout helps prevent infinite loops
    INTERNAL_TIMEOUT = 10

    def __init__(self):
        self.logger = logger()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(Client.INTERNAL_TIMEOUT)

    def udt_send(self, data, dest):
        """ send bytes to destination hosts on an unreliable channel """
        size = len(data)
        sent = 0
        while sent < size:
            to_send = min(size-sent, Client.SEND_BUF_SIZE)
            sent += self.sock.sendto(data[sent:sent+to_send], dest)
        self.logger.info('Sent {} bytes to {}'.format(sent, dest))

    def udt_recv(self, size):
        """ receive bytes from unreliable channel """
        if size > Client.RECV_BUF_SIZE:
            raise UnsupportedSizeError(
                'Cannot receive more than {} bytes'.format(Client.RECV_BUF_SIZE))
        received = b''
        while len(received) < size:
            try:
                l = len(received)
                to_recv = min(size-len(received), Client.RECV_BUF_SIZE)
                rcvd, addr = self.sock.recvfrom(to_recv)
                received += rcvd
            except socket.timeout:
                self.logger.error('Connection timed out')
                raise ReceiveError('Connection timed out')
        self.logger.info(
            'Received {} bytes from {}'.format(len(received), addr))
        return received, addr