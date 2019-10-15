from struct import unpack
from pftp.proto.proto import Header

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
        binary_repr = "{0:b}".format(seq)
        return b'0'*(Header.LEN_SEQ - len(binary_repr))+bytes(binary_repr, 'utf-8')
