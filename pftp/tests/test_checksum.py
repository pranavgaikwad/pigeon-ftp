import unittest
from pftp.proto.checksum import checksum, _chunk_bytes, _bin_add


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
        # self.assertEqual(checksum(), b'0010010110011110')