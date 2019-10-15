import unittest
from pftp.proto.proto import Segment, SegmentBuilder, Header

class ProtocolTest(unittest.TestCase):
    def test_segment_builder(self):
        data = b'10101010'
        stype = Segment.TYPE_DATA
        seq = b'10101010101010101010101010101010'
        actual = SegmentBuilder().with_data(data).with_type(stype).with_seq(seq).build()
        expected = Segment(data)
        expected.header = Header()
        expected.header.seq = seq
        expected.header.stype = stype
        expected.header.checksum = data
        self.assertEqual(expected, actual)

        actual = SegmentBuilder().with_data(data).with_seq(seq).build()
        self.assertNotEqual(expected, actual)

    def test_segment_builder_from_bytes(self):
        data = b'1010101010101010'
        checksum = data
        stype = Segment.TYPE_DATA
        seq = b'10101010101010101010101010101010'
        actual = SegmentBuilder.from_bytes(b''.join([seq,stype,checksum,data]))
        expected = Segment(data)
        expected.header.seq = seq
        expected.header.stype = stype 
        expected.header.checksum = checksum
        self.assertEqual(expected, actual)

        expected.header.checksum = b''
        self.assertNotEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()