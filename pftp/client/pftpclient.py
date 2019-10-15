import sys
from math import inf
from time import time
from collections import deque
from struct import unpack, pack
from threading import Lock, Thread
from pftp.proto.proto import Header
from pftp.client.client import Client
from pftp.utils.timeout import timeout
from pftp.proto.seq import SequenceNumberGenerator
from pftp.proto.proto import Header, SegmentBuilder, Segment


class PFTPReceiver(object):
    """ Client's representation of a receiver """

    def __init__(self, addr, timeout=0, maxsize=0):
        self.addr = addr
        self.last_seq = 0
        self.last_ack = 0
        self.last_sent_at = 0
        self.logger = logger()

    def __eq__(self, value):
        return True if self.addr == value.addr else False

    def __str__(self):
        return "{}:{}".format(self.addr[0], self.addr[1])


class PFTPClient(Client):
    """ Pigeon FTP client with SAW ARQ 

    Supports both blocking and non-blocking operations. Runs in blocking mode by default.
    """

    # this is not the ARQ timeout
    # this is a timeout on Queue. prevents from running into blocking queues
    QUEUE_TIMEOUT = 0.5

    def __init__(self, receivers, buffer=0, mss=4000, atimeout=3000, btimeout=inf):
        """ An instance of PFTPClient can be used to send data reliably.

        Args:
            receivers ([addr]): list of socket addresses. each address is a pair (host, port)
            mss (int, optional): maximum segment size. Defaults to 4000.
            atimeout (int, optional): ARQ timeout in ms. Defaults to 3000.
            btimeout (int, optional): Blocking timeout in ms. Defaults to infinity.
        """
        self.queue_msg = deque()  # a queue of bytes
        self.receivers = {str(r): r for r in receivers}
        self.mss = mss
        self.atimeout = atimeout    # ARQ timeout
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
            self.worker = Thread(target=self._rdt_send)

    def rdt_send(self, mbytes, btimeout=inf):
        """ Sends bytes to pre-configured receivers reliably

        Args:
            mbytes (bytes): byte string to send 
            btimeout (int, optional): timeout for blocking mode. Defaults to inf.
        """
        self._enqueue_bytes(mbytes)
        if self.blocking:
            return self._rdt_send(timeout=btimeout)

    def _rdt_send(self, timeout=inf):
        """ internal impl of rdt_send

        In blocking mode, _rdt_send returns number of bytes sent reliably.
        Optionally, a timeout interval can be specified to discard all bytes on timeout and return.
        In non-blocking mode, function runs in background and throws error on failure.
        """
        # no of bytes sent
        sent = 0
        start_time = time()
        stopped = lambda t: self.worker_stopped if not self.blocking else t <= 0
        while not stopped(timeout) and self.queue_msg:
            # mss = headers + data
            mss_data = self._dequeue_bytes(
                self.mss - (Header.LEN_SEQ + Header.LEN_CHECKSUM + Header.LEN_STYPE))

            current_seq, current_seq_bytes = self.seq_generator.get_next()
            current_segment = SegmentBuilder().with_data(mss_data).with_seq(
                current_seq_bytes).with_type(Segment.TYPE_DATA).build()

            sent += len(mss_data)
            timeout -= (time()-start_time)
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
                "Failed enqueuing bytes {}".format(str(sys.exc_info()[0])))

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

        # _enqueue
        # for b in list(unpack("{}c".format(len(mbytes)), mbytes)):
        #     self.queue_msg.put(b, timeout=PFTPClient.QUEUE_TIMEOUT)

        # _deque
        # all_bytes = b''
        # to_deque = min(len(all_bytes), size)
        # mbytes = all_bytes[0:to_deque]
        # append remaining size back to deque
        # if all_bytes[to_deque:]:
        # self.queue_msg.appendleft(all_bytes[to_deque:])

        # for i in range(size):
        #     mbytes += self.queue_msg.get(
        #         timeout=PFTPClient.QUEUE_TIMEOUT)
