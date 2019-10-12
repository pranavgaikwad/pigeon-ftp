# communication primitives
class MalformedSegmentError(Exception):
    pass

class MalformedHeaderError(Exception):
    pass

class Header(object):
    """ defines header structure """
    LEN_SEQ = 32
    LEN_STYPE = 16
    LEN_CHECKSUM = 16

    def __init__(self):
        self.seq = b'0'*Header.LEN_SEQ
        self.stype = b'0'*Header.LEN_STYPE
        self.checksum = b'0'*Header.LEN_CHECKSUM

    def __str__(self):
        return "{}{}{}".format(self.seq, self.stype, self.checksum)

    def __eq__(self, other):
        return True if self.seq == other.seq and self.stype == other.stype and self.checksum == other.checksum else False
    
    @staticmethod
    def from_str(header):
        h = Header()
        try:
            h.seq = header[:Header.LEN_SEQ]
            h.stype = header[Header.LEN_SEQ:Header.LEN_SEQ+Header.LEN_STYPE]
            h.checksum = header[Header.LEN_SEQ+Header.LEN_STYPE:Header.LEN_SEQ+Header.LEN_STYPE+Header.LEN_CHECKSUM]
        except (KeyError, ValueError):
            raise MalformedHeaderError()
        return h

class Segment(object):
    """ defines segment structure """
    TYPE_ACK = b'1010101010101010'
    TYPE_DATA = b'0101010101010101'
    TYPE_NONE = b'0'*Header.LEN_STYPE

    def __init__(self, data):
        self.data = data
        self.header = Header()

    def __str__(self):
        return "{}{}".format(self.header, self.data)
    
    def __eq__(self, other):
        return True if self.data == other.data and self.header == other.header else False

class SegmentBuilder(object):
    """ builds a segment """
    def __init__(self):
        self.segment = Segment(b'')
        self.seq = b'0'*Header.LEN_SEQ
        self.stype = Segment.TYPE_NONE

    def with_data(self, data):
        self.segment.data = data
        return self
    
    def with_type(self, stype):
        self.stype = stype
        return self

    def with_seq(self, seq):
        self.seq = seq
        return self

    def build(self):
        self._build_header()
        return self.segment

    def _checksum(self):
        return self.segment.data

    def _build_header(self):
        header = Header()
        header.stype = self.stype
        header.seq = self.seq
        header.checksum = self._checksum()
        self.segment.header = header

    @staticmethod
    def from_bytes(segment_bytes):
        """ generates a segment from raw bytes """
        segment = Segment(b'')
        try:
            header = Header.from_str(segment_bytes)
            segment.header = header
            segment.data = segment_bytes[Header.LEN_CHECKSUM+Header.LEN_SEQ+Header.LEN_STYPE:]
        except (KeyError, ValueError):
            raise MalformedSegmentError()
        return segment