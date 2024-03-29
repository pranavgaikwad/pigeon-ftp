from math import inf
from time import time
from collections import deque
from threading import Lock, Thread
from pftp.proto.checksum import verify
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.sequence import SequenceNumberGenerator
from pftp.proto.pftpsocket import PFTPSocket, ReceiveError
from pftp.proto.segment import SegmentBuilder, PFTPSegment as Segment, MalformedSegmentError


class PFTPReceiver(object):
    """ Client's representation of a receiver """

    def __init__(self, addr):
        self.addr = addr
        self.last_ack = -2

    def __eq__(self, value):
        return True if self.addr == value.addr else False

    def __str__(self):
        return "{}:{}".format(self.addr[0], self.addr[1])


class PFTPClient(PFTPSocket):
    """ Pigeon FTP client with SAW ARQ 

    Supports both blocking and non-blocking operations. Runs in blocking mode by default.
    """

    # this is not the ARQ timeout
    # this is a timeout on Queue. prevents from running into blocking queues
    QUEUE_TIMEOUT = 0.5

    def __init__(self, receivers, buffer=0, mss=4000, atimeout=0.1, btimeout=inf):
        """
        Args:
            receivers ([addr]): list of socket addresses. each address is a pair (host, port)
            mss (int, optional): maximum segment size. Defaults to 4000.
            atimeout (int, optional): ARQ timeout in sec. Defaults to 2.
            btimeout (int, optional): Blocking timeout in ms. Defaults to infinity.
        """
        self.queue_msg = deque()  # a queue of bytes
        self.receivers = {str(PFTPReceiver(r)): PFTPReceiver(r)
                          for r in receivers}
        self.mss = mss
        self.atimeout = atimeout  # ARQ timeout
        self.blocking = True
        self.seq_generator = SequenceNumberGenerator()
        super(PFTPClient, self).__init__()

    def setblocking(self, blocking):
        """ Sets blocking or non-blocking

        Args:
            blocking (boolean): blocking or not
        """
        self.blocking = blocking
        if not blocking:
            self.mutex_worker = Lock()
            self.worker_stopped = False
            self.worker = Thread(target=self._rdt_send, name='PFTPWorker')

    def rdt_send(self, mbytes, btimeout=inf):
        """ Sends bytes to pre-configured receivers 

        Args:
            mbytes (bytes): byte string to send 
            btimeout (int, optional): timeout for blocking mode. Defaults to inf.
        """
        self._enqueue_bytes(mbytes)
        if self.blocking:
            return self._rdt_send(timeout=btimeout)
        else:
            self.worker.start()

    def _rdt_send(self, timeout=inf):
        """ internal impl of rdt_send

        In blocking mode, _rdt_send returns number of bytes sent reliably.
        Optionally, a timeout interval can be specified to discard all bytes on timeout and return.
        In non-blocking mode, function runs in background and throws error on failure.
        """
        # from now onwards, timeout should be ARQ timeout
        self.sock.settimeout(self.atimeout)

        # no of bytes sent
        sent = 0

        def stopped(t):
            return False if not self.blocking else t <= 0

        last_seq = self.seq_generator.get_current()
        mss_data = b''
        while not stopped(timeout) and (self.queue_msg or mss_data):
            start_time = time()

            _seq = Header.size() + self.mss

            # get the next sequence number
            current_seq, current_seq_bytes = self.seq_generator.get_next(_seq)

            # only deque next bytes when last ones are sent successfully
            if last_seq != current_seq:
                mss_data = self._dequeue_bytes(self.mss)

            # build a segment
            current_segment = SegmentBuilder().with_data(mss_data).with_seq(
                current_seq_bytes).with_type(Segment.TYPE_DATA).build()

            sent_to = 0
            # send to all receivers whose acks are not received for given segment
            for r, receiver in self.receivers.items():
                if current_seq_bytes != receiver.last_ack:
                    self.logger.info(
                        'Sending {} bytes with seq {} to {}'.format(len(current_segment), current_seq, receiver.addr))
                    self.udt_send(current_segment.to_bytes(), receiver.addr)
                    sent_to += 1

            # buffer for replies
            replies = b''

            # wait for reply
            # we are expecting ACKs from n receivers
            # size of ACK = size of header; there is no data
            reply_size = sent_to * Header.size()
            verified = True

            # NOTE: Better approach for timeout?
            while len(replies) < reply_size:
                try:
                    reply, addr = self.udt_recv(Header.size())
                    reply_segment = SegmentBuilder.from_bytes(reply)
                    if not verify(reply_segment):
                        raise MalformedSegmentError
                    if reply_segment.header.seq == current_seq_bytes:
                        receiver = PFTPReceiver(addr)
                        self.receivers[str(
                            receiver)].last_ack = reply_segment.header.seq
                        self.logger.info('Received ack for seq {} from {}'.format(
                            int(reply_segment.header.seq, 2), addr))
                    else:
                        verified = False
                        self.logger.error('Bad ack from {}'.format(addr))
                    replies += reply
                except MalformedSegmentError:
                    self.logger.error('Malformed segment from {}'.format(addr))
                    verified = False
                except ReceiveError:
                    verified = False
                    break

            # undo sequence number when enough bytes are not received
            if not verified:
                self.seq_generator.undo(_seq)
            else:
                sent += len(mss_data)
                mss_data = b''

            # loop control
            last_seq = current_seq
            timeout -= (time() - start_time)
        else:
            self._stop_worker()
        return sent

    def _stop_worker(self):
        """ Sends a stop signal to the worker

        Only applicable in non-blocking mode. 
        Note that sending a stop signal does not immediately stop the worker.
        The worker will send all remaining bytes on the queue and then come to a Stop.
        """
        if not self.blocking:
            self.mutex_worker.acquire()
            self.worker_stopped = True
            self.mutex_worker.release()

    def _enqueue_bytes(self, mbytes):
        """ Enqueues bytes thread-safe on message queue one by one for further usage

        Bottleneck candidate

        Args:
            mbytes (bytes): message to send in bytes
        """
        try:
            self.queue_msg.append(mbytes)
        except IndexError:
            self.logger.error("Byte queue full")
        except MemoryError:
            raise MemoryError("Byte queue full. Insufficient memory")
        except:
            self.logger.error(
                "Failed enqueuing bytes")

    def _dequeue_bytes(self, size):
        """ Dequeues bytes thread-safe from the receiver's queue

        Bottleneck candidate

        Args:
            size (int): number of bytes to dequeue

        Returns:
            bytes: retrieved bytes
        """
        mbytes = b''
        all_bytes = b''
        try:
            # NOTE: can we improve this piece?
            while len(all_bytes) < size:
                all_bytes += self.queue_msg.popleft()
            to_deque = min(len(all_bytes), size)
            mbytes = all_bytes[0:to_deque]
            if all_bytes[to_deque:]:
                self.queue_msg.appendleft(all_bytes[to_deque:])
        except IndexError:
            self.logger.error("Byte queue empty")
            mbytes = all_bytes
        except Exception as e:
            self.logger.error(
                "Failed dequeuing bytes {}".format(str(e)))
        return mbytes
