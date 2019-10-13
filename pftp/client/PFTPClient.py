from threading import Lock
from struct import unpack, pack
from pftp.client.Client import Client
from queue import Queue, Full as FullError, Empty as EmptyError

class PFTPReceiver(object):
    """ Client's representation of a receiver """
    def __init__(self, addr, maxsize=0):
        self.addr = addr
        self.logger = logger()

    def __eq__(self, value):
        return True if self.addr == value.addr else False

    def __str__(self):
        return "{}:{}".format(self.addr[0], self.addr[1])

class PFTPClient(Client):
    """ Pigeon FTP client with SAW ARQ """
    QUEUE_TIMEOUT = 3

    def __init__(self, receivers, buffer=0, mss=4000, timeout=3000):
        """
        Args:
            receivers ([addr]): list of socket addresses. each address is a pair (host, port)
            mss (int, optional): maximum segment size. Defaults to 4000.
            timeout (int, optional): ARQ timeout in ms. Defaults to 3000.
        """
        self.stack_seq = []                     # a stack of sequence numbers
        self.queue_msg = Queue(maxsize=buffer)    # a queue of bytes
        self.mutex = Lock()                     # a mutex on byte queue
        self.receivers = {r: {} for r in receivers}

    def rdt_send(self, bytes, destination):
        return

    def _enqueue_bytes(self, mbytes):
        """ enqueues bytes thread-safe on message queue one by one for further usage

        Args:
            mbytes (bytes): message to send in bytes
        """
        self.mutex.acquire()
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
            self.mutex.release()

    def _dequeue_bytes(self, size):
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
                    timeout=PFTPClient.QUEUE_TIMEOUT)
        except EmptyError:
            self.logger.error("Queue empty for receiver {}".format(str(self)))
        except Exception as e:
            self.logger.error(
                "Failed dequeuing bytes from receiver {} : {}".format(str(self), str(e)))
        finally:
            self.mutex.release()
        return mbytes