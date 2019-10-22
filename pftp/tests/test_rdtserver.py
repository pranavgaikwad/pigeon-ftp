import unittest
from threading import Thread
from pftp.utils.logger import logger
from pftp.client.pftpclient import PFTPClient
from pftp.server.pftpserver import PFTPServer

class PFTPServerTest(unittest.TestCase):
    
    def setUp(self):
        self.server_addr = ('127.0.0.1', 9989)
        self.mss = 4000
        self.logger = logger()
        self.pftpclient = PFTPClient([self.server_addr], atimeout=0.5, mss=self.mss)
        return super().setUp()
    
    def test_rdt_recv(self):
        msg = lambda size : b'1'*size
        msg_size = 1000000
        t1 = Thread(name='RFTPClient', target=self.pftpclient.rdt_send, args=[msg(msg_size),60])
        t1.start()
        pftpserver = PFTPServer(addr=self.server_addr, mss=self.mss, err_prob=0.2)
        rcvd = b''
        for data in pftpserver.rdt_recv(timeout=40):
            rcvd += data
        t1.join()
        self.assertEqual(rcvd, msg(msg_size))
        

if __name__ == "__main__":
    unittest.main()
