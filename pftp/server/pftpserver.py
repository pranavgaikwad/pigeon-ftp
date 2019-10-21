import random
from math import inf
from time import time
from pftp.proto.checksum import verify, checksum
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
        start_time = time()
        seq_gen = SequenceNumberGenerator()
        current_seq = seq_gen.get_current()
        segment = None
        while not stopped(timeout):
            try:
                current_seq, current_seq_bytes = seq_gen.get_next()
                self.logger.info('Receiving {} bytes of data'.format(self.mss))
                data, addr = self.udt_recv(size=self.mss)

                segment = SegmentBuilder.from_bytes(data)

                # checksum
                if not verify(segment) or current_seq_bytes != segment.header.seq:
                    raise MalformedSegmentError

                # simulate error
                if not self._errored():
                    ack = SegmentBuilder().with_data(b'').with_seq(current_seq_bytes).with_type(Segment.TYPE_ACK).build()

                    self.udt_send(data=ack.to_bytes(), dest=addr)

                    # deliver data into the buffer
                    # self.deliver_data(data=segment.data)
                    yield segment.data
                
            except (MalformedSegmentError, SendError, ReceiveError):
                self.logger.info('Retrying segment with seq {}'.format(seq_gen.get_current()[0]))
                seq_gen.undo_one()
                continue
            except Exception as e:
                self.logger.info('Unexpected error in server {}'.format(str(e)))
            except:
                self.logger.info('Unknown error in server')
            finally:
                timeout -= (time() - start_time)
        else:
            yield b''