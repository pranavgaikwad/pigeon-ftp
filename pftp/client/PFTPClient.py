from struct import unpack, pack
from threading import Lock, Thread
from pftp.proto.proto import Header
from pftp.client.Client import Client
from pftp.proto.saw import StopAndWait
from queue import Queue, Full as FullError, Empty as EmptyError

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


class PFTPClient(Client, StopAndWait):
    """ Pigeon FTP client with SAW ARQ """

    # this is not the ARQ timeout
    # this is a timeout on Queue. prevents from running into blocking queues
    QUEUE_TIMEOUT = 3

    def __init__(self, receivers, buffer=0, mss=4000, timeout=3000):
        """
        Args:
            receivers ([addr]): list of socket addresses. each address is a pair (host, port)
            mss (int, optional): maximum segment size. Defaults to 4000.
            timeout (int, optional): ARQ timeout in ms. Defaults to 3000.
        """
        self.stack_seq = []                     # a stack of sequence numbers
        self.queue_msg = Queue(maxsize=buffer)  # a queue of bytes
        self.mutex_queue = Lock()               # a mutex on bytes queue
        self.mutex_worker = Lock()              # a mutex for the worker
        self.receivers = {str(r): r for r in receivers}
        self.worker_stopped = False
        self.worker = Thread(target=self._worker).start()
        self.mss = mss 
        self.timeout = timeout

    def rdt_send(self, mbytes):
        self._enqueue_bytes(mbytes)

    def _worker(self):
        """ Worker keeps watching the message queue for new messages
            An application can stop the worker by sending a stop signal to the worker.
            Note the worker does not stop immediately. It waits until all the bytes in the queue are sent reliably.
        """
        # mss includes the length of headers too
        mbytes = self._dequeue_bytes(self.mss - (Header.LEN_SEQ + Header.LEN_CHECKSUM + Header.LEN_STYPE))
        while not self.worker_stopped and not self.queue_msg.empty:

            pass

    def _stop_worker(self):
        """ Sends a stop signal to the worker
        """
        self.mutex_worker.acquire()
        self.worker_stopped = True
        self.mutex_worker.release()


    def _enqueue_bytes(self, mbytes):
        """ enqueues bytes thread-safe on message queue one by one for further usage

        Args:
            mbytes (bytes): message to send in bytes
        """
        self.mutex_queue.acquire()
        try:
            # NOTE : O(n) can we do better?
            # to MSS size logic becomes easier later, we want messages byte by byte
            for b in list(unpack("{}c".format(len(mbytes)), mbytes)):
                self.queue_msg.put(b, timeout=PFTPClient.QUEUE_TIMEOUT)
        except FullError:
            self.logger.error("Queue full for receiver {}".format(str(self)))
        except Exception as e:
            self.logger.error(
                "Failed enqueuing bytes for receiver {} : {}".format(str(self), str(e)))
        finally:
            self.mutex_queue.release()

    def _dequeue_bytes(self, size):
        """ dequeues bytes thread-safe from the receiver's queue 

        Args:
            size (int): number of bytes to dequeue

        Returns:
            bytes: retrieved bytes
        """
        mbytes = b''
        self.mutex_queue.acquire()
        try:
            # NOTE: O(n) can we do better?
            for i in range(size):
                mbytes += self.queue_msg.get(
                    timeout=PFTPClient.QUEUE_TIMEOUT)
        except EmptyError:
            self.logger.error("Queue empty for receiver {}".format(str(self)))
        except Exception as e:
            self.logger.error(
                "Failed dequeuing bytes from receiver {} : {}".format(str(self), str(e)))
        finally:
            self.mutex_queue.release()
        return mbytes