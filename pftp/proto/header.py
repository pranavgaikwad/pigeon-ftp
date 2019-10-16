class PFTPHeader(object):
    """ defines header structure """
    LEN_SEQ = 32
    LEN_STYPE = 16
    LEN_CHECKSUM = 16

    def __init__(self):
        self.seq = b'0'*PFTPHeader.LEN_SEQ
        self.stype = b'0'*PFTPHeader.LEN_STYPE
        self.checksum = b'0'*PFTPHeader.LEN_CHECKSUM

    def __str__(self):
        return "{}{}{}".format(self.seq, self.stype, self.checksum)

    def __eq__(self, other):
        return True if self.seq == other.seq and self.stype == other.stype and self.checksum == other.checksum else False

    def __len__(self):
        return len(self.seq+self.stype+self.checksum)

    def to_bytes(self):
        return self.seq+self.stype+self.checksum

    @staticmethod
    def from_bytes(header):
        h = PFTPHeader()
        try:
            h.seq = header[:PFTPHeader.LEN_SEQ]
            h.stype = header[PFTPHeader.LEN_SEQ:PFTPHeader.LEN_SEQ+PFTPHeader.LEN_STYPE]
            h.checksum = header[PFTPHeader.LEN_SEQ+PFTPHeader.LEN_STYPE:PFTPHeader.LEN_SEQ +
                                PFTPHeader.LEN_STYPE+PFTPHeader.LEN_CHECKSUM]
        except (KeyError, ValueError):
            raise MalformedHeaderError()
        return h

class MalformedHeaderError(Exception):
    pass