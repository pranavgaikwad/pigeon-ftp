import unittest
from time import time
from threading import Thread
from pftp.client.pftpclient import PFTPClient
from socket import socket, AF_INET, SOCK_DGRAM
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.segment import SegmentBuilder, PFTPSegment as Segment

class PFTPClientTest(unittest.TestCase):
    SERVER_ADDR = ('0.0.0.0', 8998)

    def setUp(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(PFTPClientTest.SERVER_ADDR)
        return super().setUp()

    def tearDown(self):
        self.sock.close()
        return super().tearDown()

    def test_enqueue_bytes(self):
        c = PFTPClient([])
        msg = b'0'*19
        c._enqueue_bytes(msg)
        self.assertEqual(len(c.queue_msg), 1)
        c._enqueue_bytes(msg)
        c._enqueue_bytes(msg)
        c._enqueue_bytes(msg)
        self.assertEqual(len(c.queue_msg), 4)

    def test_dequeue_bytes(self):
        c = PFTPClient([])        
        expected = b'0'*19
        c._enqueue_bytes(expected)
        actual = c._dequeue_bytes(19)
        self.assertEqual(actual, expected)

        c = PFTPClient([])        
        expected = b'0'*19
        c._enqueue_bytes(expected)
        actual = c._dequeue_bytes(19)
        self.assertEqual(actual, expected)

        expected = b'0'*40
        c._enqueue_bytes(expected)
        a1, e1 = c._dequeue_bytes(19), b'0'*19
        a2, e2 = c._dequeue_bytes(1), b'0'*1
        a3, e3 = c._dequeue_bytes(20), b'0'*20
        self.assertEqual(a1, e1)
        self.assertEqual(a2, e2)
        self.assertEqual(a3, e3)

        # 10 MB Test case
        expected = b'1'*10000000
        c._enqueue_bytes(expected)
        a1 = c._dequeue_bytes(10000000)
        self.assertEqual(a1, expected)
            
        # test order of dequeued bits
        expected = b'1010101001000010010101010010100100100101001001010110'
        c._enqueue_bytes(expected)
        a1, a2, a3 = c._dequeue_bytes(1), c._dequeue_bytes(10), c._dequeue_bytes(10)
        e0, e1, e2 = expected[0:1], expected[1:11], expected[11:21]
        self.assertEqual(a1, e0)
        self.assertEqual(a2, e1)
        self.assertEqual(a3, e2)


    def _test_blocking_timeout(self, timeout, delta):
        client = PFTPClient([])
        t1 = time()
        sent = client.rdt_send(b'00000'*2900, btimeout=timeout)
        t2 = time()
        client.logger.info("")
        client.logger.info("Took : {}".format(t2-t1))
        self.assertAlmostEqual(t2-t1, timeout, delta=delta)

    def test_blocking_timeout(self):
        self._test_blocking_timeout(timeout=1, delta=1)

    def test_rdt_send_blocking(self):
        # Sending a multi-segment message
        msg = b'1'*673
        client = PFTPClient([self.SERVER_ADDR], mss=400)
        t1 = Thread(target=client.rdt_send, args=[msg,])
        t1.start()
        # first segment
        recvd, addr = self.sock.recvfrom(400)
        client.logger.info('Received {} bytes from {}'.format(len(recvd), addr))
        ack = SegmentBuilder().with_seq(b'0'*32).with_type(Segment.TYPE_ACK).build()
        self.sock.sendto(ack.to_bytes(), addr)
        client.logger.info('Sending ack back to {}'.format(addr))
        e1 = SegmentBuilder().with_data(msg[:336]).with_seq(b'0'*32).with_type(Segment.TYPE_DATA).build()
        a1 = SegmentBuilder.from_bytes(recvd)
        # second segment
        recvd, addr = self.sock.recvfrom(400)
        client.logger.info('Received {} bytes from {}'.format(len(recvd), addr))
        ack = SegmentBuilder().with_seq(b'0'*31+b'1').with_type(Segment.TYPE_ACK).build()
        self.sock.sendto(ack.to_bytes(), addr)
        client.logger.info('Sending ack back to {}'.format(addr))
        e2 = SegmentBuilder().with_data(msg[336:672]).with_seq(b'0'*31+b'1').with_type(Segment.TYPE_DATA).build()
        a2 = SegmentBuilder.from_bytes(recvd)
        # third segment
        recvd, addr = self.sock.recvfrom(400)
        client.logger.info('Received {} bytes from {}'.format(len(recvd), addr))
        ack = SegmentBuilder().with_seq(b'0'*30+b'1'+b'0').with_type(Segment.TYPE_ACK).build()
        self.sock.sendto(ack.to_bytes(), addr)
        client.logger.info('Sending ack back to {}'.format(addr))
        e3 = SegmentBuilder().with_data(msg[672:]).with_seq(b'0'*31+b'1').with_type(Segment.TYPE_DATA).build()
        a3 = SegmentBuilder.from_bytes(recvd)
        
        self.assertEqual(a1.header, e1.header)
        self.assertEqual(a1.data, e1.data)
        self.assertEqual(a2.header, e2.header)
        self.assertEqual(a2.data, e2.data)
        
        t1.join()

if __name__ == "__main__":
    unittest.main()