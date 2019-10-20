import unittest
from pftp.proto.checksum import checksum
from pftp.proto.header import PFTPHeader as Header, MalformedHeaderError
from pftp.proto.segment import PFTPSegment as Segment, SegmentBuilder, MalformedSegmentError


class ProtocolTest(unittest.TestCase):
    def test_segment_builder(self):
        data = b'10101010'
        stype = Segment.TYPE_DATA
        seq = b'0'*Header.LEN_SEQ
        actual = SegmentBuilder().with_data(data).with_type(stype).with_seq(seq).build()
        expected = Segment(data)
        expected.header = Header()
        expected.header.seq = seq
        expected.header.stype = stype
        expected.header.checksum = checksum(
            header=expected.header, data=data)
        self.assertEqual(expected, actual)

        actual = SegmentBuilder().with_data(data).with_seq(seq).build()
        self.assertNotEqual(expected, actual)

    def test_segment_builder_from_bytes(self):
        data = b'1010101010101010'
        checksum = b'0'*Header.LEN_CHECKSUM
        stype = Segment.TYPE_DATA
        seq = b'1'*Header.LEN_SEQ
        actual = SegmentBuilder.from_bytes(
            b''.join([seq, stype, checksum, data]))
        expected = Segment(data)
        expected.header.seq = seq
        expected.header.stype = stype
        expected.header.checksum = checksum
        self.assertEqual(expected, actual)

        expected.header.checksum = b''
        self.assertNotEqual(expected, actual)

        self.assertEqual(len(actual.header), Header.LEN_SEQ+Header.LEN_STYPE+Header.LEN_CHECKSUM)

        self.assertRaises(MalformedSegmentError, SegmentBuilder.from_bytes, b'0'*62)

    def test_header(self):
        data = b'1010101010101010'
        checksum = b'0'*Header.LEN_CHECKSUM
        stype = Segment.TYPE_DATA
        seq = b'1'*Header.LEN_SEQ
        segment = SegmentBuilder.from_bytes(
            b''.join([seq, stype, checksum, data]))

        self.assertEqual(len(segment.header), Header.LEN_SEQ+Header.LEN_STYPE+Header.LEN_CHECKSUM)

        # test malformed header
        self.assertRaises(MalformedHeaderError, Header.from_bytes, b'0'*62)

        self.assertEqual(str(segment.header), "1"*Header.LEN_SEQ+"0101010101010101"+"0"*Header.LEN_CHECKSUM)


if __name__ == "__main__":
    unittest.main()
