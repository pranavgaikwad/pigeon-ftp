import unittest
import socket
from pftp.client.Client import Client

class ClientTest(unittest.TestCase):
    SERVER_PORT = 9000
    SERVER_HOST = '0.0.0.0'

    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ClientTest.SERVER_HOST, ClientTest.SERVER_PORT))
        return super().setUp()

    def tearDown(self):
        self.sock.close()
        return super().tearDown()

    def test_udt_send(self):
        data = b'1'*16
        client = Client()
        client.udt_send(data, ClientTest.SERVER_HOST, ClientTest.SERVER_PORT)
        received, addr = self.sock.recvfrom(1024)
        self.assertEquals(received, data)

        data = b'0'*1025
        client.udt_send(data, ClientTest.SERVER_HOST, ClientTest.SERVER_PORT)
        received, addr = self.sock.recvfrom(1024)
        self.assertEquals(data[:1024], received)

        # udp packet limits on packet size
        data = b'0'*65535
        client.udt_send(data, ClientTest.SERVER_HOST, ClientTest.SERVER_PORT)
        received, addr = self.sock.recvfrom(65535)
        len_recv = len(received)
        # server should only receive first 9216 bytes here
        # needs to be handled in udt_recv to get all data
        self.assertNotEquals(data, received)

if __name__ == "__main__":
    unittest.main()