import unittest
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.sequence import SequenceNumberGenerator


class SequenceGeneratorTest(unittest.TestCase):

    def test_seq_next(self):
        s = SequenceNumberGenerator()
        a2, a2b = s.get_next()
        a3, a3b = s.get_current()
        a4, a4b = s.get_next()
        a5, a5b = s.get_prev()
        self.assertEqual(a2, 0)
        self.assertEqual(a3, 0)
        self.assertEqual(a4, 1)
        self.assertEqual(a5, 0)

        seq_len = Header.LEN_SEQ
        e1b, e2b, e3b = b'0'*seq_len, b'0'*seq_len, b'0'*(seq_len-1) + b'1'
        self.assertEqual(a2b, e2b)
        self.assertEqual(a4b, e3b)
        self.assertEqual(a5b, e2b)

    def test_undo_one(self):
        s = SequenceNumberGenerator()
        a1, _ = s.get_next()
        self.assertEqual(a1, 0)
        a2, _ = s.undo_one()
        self.assertEqual(a2, -1)


if __name__ == "__main__":
    unittest.main()
