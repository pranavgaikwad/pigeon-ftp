import unittest
from pftp.client.PFTPClient import PFTPClient

class PFTPClientTest(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def test_enqueue_bytes(self):
        c = PFTPClient([])
        msg = b'0'*19
        c._enqueue_bytes(msg)
        self.assertEquals(c.queue_msg.qsize(), len(msg))
        c._enqueue_bytes(msg)
        c._enqueue_bytes(msg)
        c._enqueue_bytes(msg)
        self.assertEquals(c.queue_msg.qsize(), len(msg)*4)

    def test_dequeue_bytes(self):
        c = PFTPClient([])        
        expected = b'0'*19
        c._enqueue_bytes(expected)
        actual = c._dequeue_bytes(19)
        self.assertEquals(actual, expected)

        # test order of dequeued bits
        expected = b'1010101001000010010101010010100100100101001001010110'
        c._enqueue_bytes(expected)
        a1, a2, a3 = c._dequeue_bytes(1), c._dequeue_bytes(10), c._dequeue_bytes(10)
        e0, e1, e2 = expected[0:1], expected[1:11], expected[11:21]
        self.assertEquals(a1, e0)
        self.assertEquals(a2, e1)
        self.assertEquals(a3, e2)

if __name__ == "__main__":
    unittest.main()