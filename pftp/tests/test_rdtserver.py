import unittest
from threading import Thread
from pftp.utils.logger import logger
from pftp.client.pftpclient import PFTPClient
from pftp.server.pftpserver import PFTPServer

class PFTPServerTest(unittest.TestCase):
    
    def setUp(self):
        self.server_addr = ('127.0.0.1', 9989)
        self.mss = 8192
        self.logger = logger()
        self.pftpclient = PFTPClient([self.server_addr], atimeout=0.5, mss=self.mss)
        return super().setUp()
    
    def test_rdt_recv(self):
        msg = lambda size : b'1'*size
        msg_size = 10000000
        t1 = Thread(name='RFTPClient', target=self.pftpclient.rdt_send, args=[msg(msg_size),60])
        t1.start()
        pftpserver = PFTPServer(addr=self.server_addr, mss=self.mss)
        rcvd = b''
        for data in pftpserver.rdt_recv(timeout=5):
            rcvd += data
        t1.join()
        self.assertEqual(rcvd, msg(msg_size))
        

if __name__ == "__main__":
    unittest.main()
