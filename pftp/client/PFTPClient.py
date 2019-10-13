from queue import Queue
from threading import Lock
from pftp.client.Client import Client


class PFTPReceiver(object):
    """ Client's representation of a receiver """

    QUEUE_TIMEOUT = 3

    def __init__(self, addr):
        self.addr = addr
        self.stack_seq = []        # a stack of sequence numbers
        self.queue_msg = Queue()   # a queue of bytes
        self.mutex = Lock()        # a mutex on byte queue

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
                self.queue_msg.put(mbytes, timeout=PFTPReceiver.QUEUE_TIMEOUT)
        except Queue.full:
            self.logger.error('Queue full for receiver {}'.format(str(self)))
        except Exception as e:
            self.logger.error('Failed enqueuing bytes for receiver {} : {}'.format(str(self), str(e)))
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
                mbytes += self.queue_msg.get(timeout=PFTPReceiver.QUEUE_TIMEOUT)
        except Queue.empty:
            self.logger.error('Queue empty for receiver {}'.format(str(self)))
        except Exception as e:
            self.logger.error('Failed dequeuing bytes from receiver {} : {}'.format(str(self), str(e)))
        finally:
            self.mutex.release()
        return mbytes

    def __eq__(self, value):
        return True if self.host == value.host and self.port == value.port and self.addr == value.addr else False

    def __str__(self, value):
        return "{}:{}".format(self.host, self.port)


class PFTPClient(Client):
    """ Pigeon FTP client with SAW ARQ """

    def __init__(self, receivers, mss=4000, timeout=3000):
        """
        Args:
            receivers ([PFTPReceiver]): list of receivers
            mss (int, optional): maximum segment size. Defaults to 4000.
            timeout (int, optional): ARQ timeout in ms. Defaults to 3000.
        """
        self.receivers = {r: {} for r in receivers}

    def rdt_send(self, bytes, destination):
        return
