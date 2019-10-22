import unittest
from threading import Thread
from pftp.utils.logger import logger
from pftp.client.pftpclient import PFTPClient
from pftp.server.pftpserver import PFTPServer

class PFTPServerTest(unittest.TestCase):
    
    def setUp(self):
        self.server_addr = [('127.0.0.1', 9989), ('127.0.0.1', 9988)]
        self.mss = 8000
        self.logger = logger()
        self.pftpclient = PFTPClient(self.server_addr, atimeout=0.5, mss=self.mss)
        return super().setUp()

    def _test_rdt_recv(self, addr, msg, timeout):
        pftpserver = PFTPServer(addr=addr, mss=self.mss, err_prob=0.1)
        rcvd = b''
        for data in pftpserver.rdt_recv(timeout=timeout):
            rcvd += data
        self.assertEqual(rcvd, msg) 

    def test_rdt_recv(self):
        msg = lambda size : b'1'*size
        msg_size = 10000
        sender_thread = Thread(name='RFTPClient', target=self.pftpclient.rdt_send, args=[msg(msg_size),60])
        sender_thread.start()
        receiver_threads = []
        for idx, i in enumerate(self.server_addr):
            receiver_threads.append(Thread(name='{}'.format(i), target=self._test_rdt_recv, args=[i, msg(msg_size), 4]))
        for t in receiver_threads:
            t.start()
        for t in receiver_threads:
            t.join()
        sender_thread.join()
        

if __name__ == "__main__":
    unittest.main()
