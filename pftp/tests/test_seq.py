import unittest
from pftp.proto.proto import Header
from pftp.proto.seq import SequenceNumberGenerator

class SequenceGeneratorTest(unittest.TestCase):

    def test_seq_next(self):
        s = SequenceNumberGenerator()
        a1, a1b = s.get_current()
        a2, a2b = s.get_next()
        a3, a3b = s.get_current()
        self.assertEquals(a1, 0)
        self.assertEquals(a2, 1)
        self.assertEquals(a3, 1)

        seq_len = Header.LEN_SEQ
        e1b, e2b, e3b = b'0'*seq_len, b'0'*(seq_len-1) + b'1', b'0'*(seq_len-1) + b'1'
        self.assertEquals(a1b, e1b)
        self.assertEquals(a2b, e2b) 
        self.assertEquals(a3b, e3b)