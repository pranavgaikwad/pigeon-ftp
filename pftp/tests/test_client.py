import unittest
import socket
import threading
from pftp.proto.pftpsocket import PFTPSocket as Client, UnsupportedSizeError 

class ClientTest(unittest.TestCase):
    SERVER_ADDR = ('0.0.0.0', 9000)

    def setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(ClientTest.SERVER_ADDR)
        return super().setUp()

    def tearDown(self):
        self.sock.close()
        return super().tearDown()

    def test_udt_send(self):
        data = b'1'*16
        client = Client()
        client.udt_send(data, ClientTest.SERVER_ADDR)
        received, addr = self.sock.recvfrom(1024)
        self.assertEqual(received, data)

        clients = [Client()]*10
        threads = [threading.Thread(target=clients[i].udt_send, args=[data, ClientTest.SERVER_ADDR]) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        received = []
        for i in range(10):
            rcvd, addr = self.sock.recvfrom(1024)
            received.append(rcvd)
        self.assertEqual([data]*10, received)

        data = b'0'*1025
        client.udt_send(data, ClientTest.SERVER_ADDR)
        received, addr = self.sock.recvfrom(1024)
        self.assertEqual(data[:1024], received)

        # udp packet limits on packet size
        data = b'0'*65535
        client.udt_send(data, ClientTest.SERVER_ADDR)
        received = b''
        while len(received) < 65535:
            try: 
                self.sock.settimeout(10)
                rcvd, addr = self.sock.recvfrom(65535)
                received += rcvd
            except socket.timeout:
                break
        len_recv = len(received)
        self.assertEqual(data, received)

    def test_udt_recv(self):
        data = b'1'*10
        client = Client()
        client.udt_send(data, ClientTest.SERVER_ADDR)
        d, addr = self.sock.recvfrom(1024)
        self.sock.sendto(d, addr)
        received, addr = client.udt_recv(11)
        self.assertEqual(received, data)

        data = b'1'*9217
        client.udt_send(data, ClientTest.SERVER_ADDR)
        d, addr = self.sock.recvfrom(1024)
        client.udt_send(data, addr)
        received, addr = client.udt_recv(9217)
        l = len(received)
        self.assertEqual(received, data)

        self.assertRaises(UnsupportedSizeError, client.udt_recv, Client.RECV_BUF_SIZE+1)

if __name__ == "__main__":
    unittest.main()