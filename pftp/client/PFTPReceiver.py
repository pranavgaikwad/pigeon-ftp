from queue import Queue, Full as FullError, Empty as EmptyError
from threading import Lock
from pftp.utils.logger import logger


class PFTPReceiver(object):
    """ Client's representation of a receiver """

    QUEUE_TIMEOUT = 3

    def __init__(self, addr):
        self.addr = addr
        self.stack_seq = []        # a stack of sequence numbers
        self.queue_msg = Queue()   # a queue of bytes
        self.mutex = Lock()        # a mutex on byte queue
        self.logger = logger()

    def enqueue_bytes(self, mbytes):
        """ enqueues bytes thread-safe on message queue one by one for further usage

        Args:
            mbytes (bytes): message to send in bytes
        """
        self.mutex.acquire()
        try:
            # NOTE : O(n) can we do better?
            # to MSS size logic becomes easier later, we want messages byte by byte
            for b in mbytes:
                self.queue_msg.put(b, timeout=PFTPReceiver.QUEUE_TIMEOUT)
        except FullError:
            self.logger.error('Queue full for receiver {}'.format(str(self)))
        except Exception as e:
            self.logger.error(
                'Failed enqueuing bytes for receiver {} : {}'.format(str(self), str(e)))
        finally:
            self.mutex.release()

    def dequeue_bytes(self, size):
        """ dequeues bytes thread-safe from the receiver's queue 

        Args:
            size (int): number of bytes to dequeue

        Returns:
            bytes: retrieved bytes
        """
        mbytes = b''
        self.mutex.acquire()
        try:
            # NOTE: O(n) can we do better?
            for i in range(size):
                mbytes += self.queue_msg.get(
                    timeout=PFTPReceiver.QUEUE_TIMEOUT)
        except EmptyError:
            self.logger.error('Queue empty for receiver {}'.format(str(self)))
        except Exception as e:
            self.logger.error(
                'Failed dequeuing bytes from receiver {} : {}'.format(str(self), str(e)))
        finally:
            self.mutex.release()
        return mbytes

    def __eq__(self, value):
        return True if self.host == value.host and self.port == value.port and self.addr == value.addr else False

    def __str__(self, value):
        return "{}:{}".format(self.host, self.port)
