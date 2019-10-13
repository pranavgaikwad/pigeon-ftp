# stop-and-wait protocol
from abc import ABCMeta, abstractmethod

class StopAndWait(object):
    __metaclass__ = ABCMeta

    @classmethod
    def version(cls): return "1.0"

    @abstractmethod
    def send(self): raise NotImplementedError

    @abstractmethod
    def wait(self): raise NotImplementedError

    @abstractmethod
    def timeout(self): raise NotImplementedError
