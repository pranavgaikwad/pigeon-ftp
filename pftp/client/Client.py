import socket

class Client(object):
    """ generic UDP client """
    RECV_BUF_SIZE = 4096
    SEND_BUF_SIZE = 9216

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def udt_send(self, data, dest_ip, dest_port):
        """ interface to send bytes to destination hosts on an unreliable channel """
        size = len(data)
        sent = 0
        while sent < size:
            to_send = min(size-sent, Client.SEND_BUF_SIZE)
            sent += self.sock.sendto(data[sent:sent+to_send], (dest_ip, dest_port))
    
    def udt_recv(self):
        """ interface to receive bytes from unreliable channel """
        raise NotImplementedError