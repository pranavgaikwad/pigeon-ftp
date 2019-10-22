import errno
import socket
from time import sleep
from struct import pack, unpack
from pftp.utils.logger import logger


class SendError(Exception):
    pass


class ReceiveError(Exception):
    pass


class UnsupportedSizeError(Exception):
    pass


class PFTPSocket(object):
    """ A generic UDP socket with udt_send and udt_recv
    """

    # MSS value cannot be higher than this
    RECV_BUF_SIZE = 65535
    SEND_BUF_SIZE = 8192

    # this is not the ARQ timeout
    # internal timeout helps prevent infinite loops
    INTERNAL_TIMEOUT = 3

    def __init__(self):
        self.logger = logger()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(PFTPSocket.INTERNAL_TIMEOUT)

    def udt_send(self, data, dest):
        """ Sends given data on an un-reliable channel

        Args:
            data (bytes): bytes like data to send
            dest (tuple): addr of destination (host, port)

        Raises:
            SendError: failed sending data

        Returns:
            int: number of bytes sent
        """
        size = len(data)
        sent = 0
        while sent < size:
            to_send = min(size-sent, PFTPSocket.SEND_BUF_SIZE)
            try:
                sent += self.sock.sendto(data[sent:sent+to_send], dest)
            # OS socket buffers full
            except socket.error as e:
                if e.errno == errno.EAGAIN:
                    sleep(0.1)
                    continue
                raise SendError('Failed sending bytes')
        self.logger.info('Sent {} bytes to {}'.format(sent, dest))
        return sent

    def udt_recv(self, size):
        """ Receives UDP datagrams from un-reliable channel

        Args:
            size (int): size of data to receive

        Raises:
            UnsupportedSizeError: receive size exceeds maximum buffer
            ReceiveError: failed receiving

        Returns:
            tuple (msg, addr): received message and address of source
        """
        if size > PFTPSocket.RECV_BUF_SIZE:
            raise UnsupportedSizeError(
                'Cannot receive more than {} bytes'.format(PFTPSocket.RECV_BUF_SIZE))
        received = b''
        try:
            while len(received) < size:
                try:
                    to_recv = min(PFTPSocket.SEND_BUF_SIZE, size)
                    rcvd, addr = self.sock.recvfrom(PFTPSocket.SEND_BUF_SIZE)
                    received += rcvd
                    self.logger.info(
                        'Received {} bytes from {}'.format(len(received), addr))
                    if len(rcvd) < to_recv:
                        break
                except socket.timeout:
                    self.logger.info('Socket timed out')
                    raise ReceiveError
        except:
            raise ReceiveError('Unexpected error')
        return received, addr
