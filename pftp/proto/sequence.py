from struct import unpack
from pftp.proto.header import PFTPHeader as Header


class SequenceNumberGenerator(object):
    """ Helps generate sequence numbers reliably 

    Additionally, provides conversion to / from bytes to / from integer
    """

    def __init__(self):
        self.seq = -1

    def get_next(self):
        self.seq += 1
        return self.seq, self.from_int(self.seq)

    def get_prev(self):
        return self.seq-1, self.from_int(self.seq-1)

    def get_current(self):
        return self.seq, self.from_int(self.seq)

    def from_int(self, seq):
        return ("{0:0%db}" % Header.LEN_SEQ).format(seq).encode()

    def undo_one(self):
        self.seq -= 1
        return self.seq, self.from_int(self.seq)
