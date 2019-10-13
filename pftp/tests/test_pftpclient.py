import unittest
from pftp.client.PFTPClient import PFTPReceiver, PFTPClient

class PFTPClientTest(unittest.TestCase):
    def test_enqueue_pftp_receiver(self):
        msg = b'0'*19
        r = PFTPReceiver(('0.0.0.0', 9999))
        r.enqueue_bytes(msg)
        self.assertEquals(r.queue_msg.qsize(), len(msg))
        r.enqueue_bytes(msg)
        r.enqueue_bytes(msg)
        r.enqueue_bytes(msg)
        self.assertEquals(r.queue_msg.qsize(), len(msg)*4)


    def test_dequeue_pftp_receiver(self):
        msg = b'0'*19
        r = PFTPReceiver(('0.0.0.0', 9999))
        r.enqueue_bytes(msg)
        msg = r.dequeue_bytes(76)
        print(msg)

if __name__ == "__main__":
    unittest.main()