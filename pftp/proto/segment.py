from pftp.proto.checksum import checksum
from pftp.proto.header import PFTPHeader, MalformedHeaderError

class PFTPSegment(object):
    TYPE_ACK = b'1010101010101010'
    TYPE_DATA = b'0101010101010101'
    TYPE_NONE = b'0'*PFTPHeader.LEN_STYPE

    def __init__(self, data):
        self.data = data
        self.header = PFTPHeader()

    def __str__(self):
        return "{}{}".format(self.header, self.data)

    def __eq__(self, other):
        return True if self.data == other.data and self.header == other.header else False

    def to_bytes(self):
        return self.header.to_bytes() + self.data

    def __len__(self):
        return len(self.header) + len(self.data)

class MalformedSegmentError(Exception):
    pass

class SegmentBuilder(object):
    """ builds a segment """

    def __init__(self):
        self.segment = PFTPSegment(b'')
        self.seq = b'0'*PFTPHeader.LEN_SEQ
        self.stype = PFTPSegment.TYPE_NONE

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

    def _build_header(self):
        header = PFTPHeader()
        header.stype = self.stype
        header.seq = self.seq
        header.checksum = checksum(header=header, data=self.segment.data)
        self.segment.header = header

    @staticmethod
    def from_bytes(segment_bytes):
        """ generates a segment from raw bytes """
        segment = PFTPSegment(b'')
        try:
            header = PFTPHeader.from_bytes(segment_bytes)
            segment.header = header
            segment.data = segment_bytes[PFTPHeader.LEN_CHECKSUM +
                                         PFTPHeader.LEN_SEQ+PFTPHeader.LEN_STYPE:]
        except (KeyError, ValueError, MalformedHeaderError):
            raise MalformedSegmentError()
        return segment