# communication primitives
class UnmadeSegmentError(Exception):
    pass

class Header(object):
    """ defines header structure """
    def __init__(self):
        self.seq = b'00000000000000000000000000000000'
        self.stype = b''
        self.checksum = b'00000000000'

    def __str__(self):
        pass

class Segment(object):
    """ defines segment structure """
    TYPE_ACK = b'1010101010101010'
    TYPE_DATA = b'0101010101010101'

    def __init__(self, data, stype=b''):
        self.data = data
        self.stype = stype
        self.header = Header()

    def __str__(self):
        pass

    @staticmethod
    def from_str(self):
        pass

class SegmentBuilder(object):
    """ builds a segment """
    def __init__(self):
        self.segment = Segment(b'')
        self.seq = b''

    def with_data(self, data):
        self.segment.data = data
        return self
    
    def with_type(self, stype):
        self.segment.stype = stype
        return self

    def with_seq(self, seq):
        self.seq = seq
        return self

    def build(self):
        self._build_header()
        return self.segment

    def _checksum(self):
        return self.data

    def _build_header(self):
        header = Header()
        header.stype = self.segment.stype
        header.seq = self.seq
        header.checksum = self._checksum()
        self.segment.header = header
