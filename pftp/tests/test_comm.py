import unittest
import unittest
from pftp.proto.comm import Segment, SegmentBuilder, Header

class CommTest(unittest.TestCase):
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
        self.assertEquals(expected, actual)

        actual = SegmentBuilder().with_data(data).with_seq(seq).build()
        self.assertNotEquals(expected, actual)

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
        self.assertEquals(expected, actual)

        expected.header.checksum = b''
        self.assertNotEquals(expected, actual)


if __name__ == "__main__":
    unittest.main()