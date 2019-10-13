import unittest
from pftp.client.PFTPReceiver import PFTPReceiver

class PFTPReceiverTest(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def test_enqueue_pftp_receiver(self):
        r = PFTPReceiver(('0.0.0.0', 9999))
        msg = b'0'*19
        r.enqueue_bytes(msg)
        self.assertEquals(r.queue_msg.qsize(), len(msg))
        r.enqueue_bytes(msg)
        r.enqueue_bytes(msg)
        r.enqueue_bytes(msg)
        self.assertEquals(r.queue_msg.qsize(), len(msg)*4)

    def test_dequeue_pftp_receiver(self):
        r = PFTPReceiver(('0.0.0.0', 9999))        
        expected = b'0'*19
        r.enqueue_bytes(expected)
        actual = r.dequeue_bytes(19)
        self.assertEquals(actual, expected)

        # test order of dequeued bits
        expected = b'1010101001000010010101010010100100100101001001010110'
        r.enqueue_bytes(expected)
        a1, a2, a3 = r.dequeue_bytes(1), r.dequeue_bytes(10), r.dequeue_bytes(10)
        e0, e1, e2 = expected[0:1], expected[1:11], expected[11:21]
        self.assertEquals(a1, e0)
        self.assertEquals(a2, e1)
        self.assertEquals(a3, e2)

if __name__ == "__main__":
    unittest.main()