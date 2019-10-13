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
        actual = r.dequeue_bytes(76)
        self.assertEquals(actual, expected)

        # test order of dequeued bits
        expected = b'1010101001000010010101010010100100100101001001010110'
        r.enqueue_bytes(expected)
        a1 = r.dequeue_bytes(1)
        a2 = r.dequeue_bytes(10)
        a3 = r.dequeue_bytes(10)
        self.assertEquals(a1, expected[0])
        self.assertEquals(a2, expected[1:11])
        self.assertEquals(a3, expected[11:21])


if __name__ == "__main__":
    unittest.main()