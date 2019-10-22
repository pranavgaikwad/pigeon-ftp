import random
from math import inf
from time import time
from pftp.proto.checksum import verify, checksum
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.sequence import SequenceNumberGenerator
from pftp.proto.pftpsocket import PFTPSocket, SendError, ReceiveError
from pftp.proto.segment import PFTPSegment as Segment, SegmentBuilder, MalformedSegmentError


class PFTPServer(PFTPSocket):
    """ PFTPServer : always running server receives messages from PFTPClient """

    def __init__(self, addr, mss=4000, err_prob=0.00):
        """ A server runs at an well known addr

        Args:
            addr (tuple): address to bind. it's a pair (host, port). defaults to 4000
            err_prob (float): probability of packet loss. defaults to 0
        """
        super(PFTPServer, self).__init__()
        self.addr = addr
        self.sock.bind(addr)
        self.mss = mss
        self.err_prob = err_prob

    def _errored(self):
        return True if self.err_prob >= random.random() else False

    def deliver_data(self, data):
        """ yields received data """
        self.logger.info('Delivering data')
        yield data

    def rdt_recv(self, timeout=inf):
        """ starts the server """
        def stopped(t): return True if t <= 0 else False
        seq_gen = SequenceNumberGenerator()
        current_seq = seq_gen.get_current()
        while not stopped(timeout):
            start_time = time()
            try:
                current_seq, current_seq_bytes = seq_gen.get_next()
                self.logger.info('Receiving {} bytes of data'.format(self.mss+Header.size()))
                data, addr = self.udt_recv(size=self.mss+Header.size())

                segment = SegmentBuilder.from_bytes(data)

                # checksum
                if not verify(segment) or (current_seq_bytes != segment.header.seq):
                    raise MalformedSegmentError
                
                # simulate error
                if self._errored():
                    self.logger.info('Simulating error')
                    raise MalformedSegmentError

                ack = SegmentBuilder().with_data(b'').with_seq(current_seq_bytes).with_type(Segment.TYPE_ACK).build()

                self.udt_send(data=ack.to_bytes(), dest=addr)

                # deliver data to upper layer
                yield segment.data
            except (MalformedSegmentError, SendError, ReceiveError):
                seq_gen.undo_one()
                self.logger.info('Retrying segment with seq {}'.format(seq_gen.get_current()[0]))
            except Exception as e:
                self.logger.info('Unexpected error in server {}'.format(str(e)))
            except:
                self.logger.info('Unknown error in server')
            finally:
                timeout -= time() - start_time
        else:
            yield b''