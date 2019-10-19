import random
import unittest
from time import time
from threading import Thread
from pftp.utils.logger import logger
from pftp.proto.checksum import _chunk_bytes
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.sequence import SequenceNumberGenerator
from pftp.client.pftpclient import PFTPClient, PFTPReceiver
from socket import socket, AF_INET, SOCK_DGRAM, timeout as socketTimeout
from pftp.proto.segment import SegmentBuilder, PFTPSegment as Segment, MalformedSegmentError

class PFTPClientTest(unittest.TestCase):
    SERVER_ADDR = ('127.0.0.1', 8998)

    def setUp(self):
        self.logger = logger()
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(PFTPClientTest.SERVER_ADDR)
        self.sock.settimeout(30)
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

    def test_eq_receiver(self):
        p1, p2 = PFTPReceiver(addr=('', 0)), PFTPReceiver(addr=('', 0))
        self.assertEqual(p1, p2)

        p1.addr = ('0.0.0.0', 998)
        self.assertNotEqual(p1, p2)

        p2.addr = ('0.0.0.0', 998)
        self.assertEqual(p1, p2)

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

    def _receive_segment(self, mss):
        recvd, addr = self.sock.recvfrom(mss)
        self.logger.info('Received {} bytes from {}'.format(len(recvd), addr))
        return SegmentBuilder.from_bytes(recvd), addr

    def _send_ack_to(self, seq, addr):
        ack = SegmentBuilder().with_seq(seq).with_type(Segment.TYPE_ACK).build()
        self.sock.sendto(ack.to_bytes(), addr)
        self.logger.info('Sending ack for seq {} back to {}'.format(int(ack.header.seq, 2), addr))

    def test_rdt_send_non_blocking(self):
        # non blocking mode test
        mss = 400
        client = PFTPClient([self.SERVER_ADDR], mss=mss)
        msg = lambda size: b'1'*size

        msg_size = 673
        seq_gen = SequenceNumberGenerator()
        client.setblocking(False)
        client.rdt_send(msg(msg_size))
        # start a blocking send
        # check all segments
        for chunk in _chunk_bytes(msg(msg_size), mss-Header.size()):
            actual, addr = self._receive_segment(mss)
            _, seq = seq_gen.get_next()
            expected = SegmentBuilder().with_data(chunk).with_seq(seq).with_type(Segment.TYPE_DATA).build()
            self._send_ack_to(seq=actual.header.seq, addr=addr)
            self.assertEqual(actual, expected)

    def test_rdt_send_saw_1(self):
        # SAW Test : Level 1
        # send three segments from server. check for in-order delivery.
        # send ACKs back to server. leave it at that.
        mss = 400
        client = PFTPClient([self.SERVER_ADDR], mss=mss)
        msg = lambda size: b'1'*size

        msg_size = 673
        seq_gen = SequenceNumberGenerator()
        # start a blocking send
        t1 = Thread(target=client.rdt_send, args=[msg(msg_size),])
        t1.start()
        # check all segments
        for chunk in _chunk_bytes(msg(msg_size), mss-Header.size()):
            actual, addr = self._receive_segment(mss)
            _, seq = seq_gen.get_next()
            expected = SegmentBuilder().with_data(chunk).with_seq(seq).with_type(Segment.TYPE_DATA).build()
            self._send_ack_to(seq=actual.header.seq, addr=addr)
            self.assertEqual(actual, expected)
        t1.join()

    def test_rdt_send_saw_2(self):
        # SAW Test : Level 2
        # send one segment from server. check for delivery.
        # do not send back ACK. wait for retry packet. use blocking timeout to return from loop
        mss = 400
        client = PFTPClient([self.SERVER_ADDR], mss=mss)
        msg = lambda size: b'1'*size

        msg_size = 336
        seq_gen = SequenceNumberGenerator()
        # start a blocking send
        t1 = Thread(target=client.rdt_send, args=[msg(msg_size),3])
        t1.start()
        # receive first segment 
        actual, addr = self._receive_segment(mss)
        _, seq = seq_gen.get_next()
        expected = SegmentBuilder().with_data(msg(msg_size)).with_seq(seq).with_type(Segment.TYPE_DATA).build()
        self.assertEqual(actual, expected)
        # check retried segment 
        actual, addr = self._receive_segment(mss)
        _, seq = seq_gen.get_current()  # Notice sequence Number here
        expected = SegmentBuilder().with_data(msg(msg_size)).with_seq(seq).with_type(Segment.TYPE_DATA).build()
        self.assertEqual(actual, expected)
        t1.join()

    def test_rdt_send_saw_3(self):
        # SAW Test : Level 3
        # simulate failures. check for retry.
        mss = 4000
        client = PFTPClient([self.SERVER_ADDR], mss=mss, atimeout=0.5)
        msg = lambda size: b'1'*size

        msg_size = 8000
        # start a blocking send
        t1 = Thread(target=client.rdt_send, args=[msg(msg_size)])
        rcvd_msg = b''
        t1.start()
        while len(rcvd_msg) < msg_size:
            try: 
                segment, addr = self._receive_segment(mss)
            except (socketTimeout, MalformedSegmentError):
                continue
            if bool(random.getrandbits(1)):
                self._send_ack_to(seq=segment.header.seq, addr=addr)
                rcvd_msg += segment.data
        t1.join()
        # finally make sure all 8000 bytes are received
        self.assertEqual(len(rcvd_msg), msg_size)



if __name__ == "__main__":
    unittest.main()