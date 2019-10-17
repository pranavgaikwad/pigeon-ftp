import unittest
from pftp.proto.segment import SegmentBuilder
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.checksum import checksum, _chunk_bytes, _bin_add, _compl, verify


class ChecksumTest(unittest.TestCase):

    def test_chunk_bytes(self):
        data = b'1010'*17
        chunks = [i for i in _chunk_bytes(data, 16)]
        self.assertEqual(len(chunks), 5)

    def test_bin_add(self):
        b1, b2 = 0b1000000110110101, 0b1010001111101001
        self.assertEqual(_bin_add(
            b1, b2), 0b0010010110011111)

    def test_checksum(self):
        b1, b2 = 0b1000000110110101, 0b1010001111101001
        self.assertEqual(_bin_add(
            b1, b2), 0b0010010110011111)
        bin_add = _bin_add(0b1000000110110101, 0b1010001111101001)
        bin_add = _bin_add(bin_add, 0b1101101001100000)
        self.assertEqual(bin_add, 0b1111111111111111)

    def test_compl(self):
        expected = 0b0010010110011111
        actual = _compl(0b1101101001100000)
        self.assertEqual(expected, actual)

    def test_verify(self):
        segment = SegmentBuilder().with_seq(b'0'*Header.LEN_SEQ).with_type(b'0'*Header.LEN_STYPE).build()
        self.assertTrue(verify(segment))
