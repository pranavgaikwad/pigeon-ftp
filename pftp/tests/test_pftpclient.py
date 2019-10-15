import unittest
from time import time
from pftp.client.pftpclient import PFTPClient

class PFTPClientTest(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def test_enqueue_bytes(self):
        c = PFTPClient([])
        msg = b'0'*19
        c._enqueue_bytes(msg)
        self.assertEquals(len(c.queue_msg), 1)
        c._enqueue_bytes(msg)
        c._enqueue_bytes(msg)
        c._enqueue_bytes(msg)
        self.assertEquals(len(c.queue_msg), 4)

    def test_dequeue_bytes(self):
        c = PFTPClient([])        
        expected = b'0'*19
        c._enqueue_bytes(expected)
        actual = c._dequeue_bytes(19)
        self.assertEquals(actual, expected)

        c = PFTPClient([])        
        expected = b'0'*19
        c._enqueue_bytes(expected)
        actual = c._dequeue_bytes(19)
        self.assertEquals(actual, expected)

        expected = b'0'*40
        c._enqueue_bytes(expected)
        a1, e1 = c._dequeue_bytes(19), b'0'*19
        a2, e2 = c._dequeue_bytes(1), b'0'*1
        a3, e3 = c._dequeue_bytes(20), b'0'*20
        self.assertEquals(a1, e1)
        self.assertEquals(a2, e2)
        self.assertEquals(a3, e3)

        # 10 MB Test case
        expected = b'1'*10000000
        c._enqueue_bytes(expected)
        a1 = c._dequeue_bytes(10000000)
        self.assertEquals(a1, expected)
            
        # test order of dequeued bits
        expected = b'1010101001000010010101010010100100100101001001010110'
        c._enqueue_bytes(expected)
        a1, a2, a3 = c._dequeue_bytes(1), c._dequeue_bytes(10), c._dequeue_bytes(10)
        e0, e1, e2 = expected[0:1], expected[1:11], expected[11:21]
        self.assertEquals(a1, e0)
        self.assertEquals(a2, e1)
        self.assertEquals(a3, e2)


    def _test_blocking_timeout(self, timeout, delta):
        client = PFTPClient([])
        t1 = time()
        sent = client.rdt_send(b'00000'*2900000000, btimeout=timeout)
        t2 = time()
        client.logger.info("")
        client.logger.info("Took : {}".format(t2-t1))
        self.assertAlmostEquals(t2-t1, timeout, delta=delta)

    def test_blocking_timeout(self):
        self._test_blocking_timeout(timeout=10, delta=10)

    def test_rdt_send_blocking(self):
        msg = b'010101'*2000
        client = PFTPClient([], mss=400, btimeout=20)
        sent = client.rdt_send(msg)
        self.assertEquals(sent, len(msg))

if __name__ == "__main__":
    unittest.main()