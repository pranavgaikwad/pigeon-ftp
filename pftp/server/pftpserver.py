import random
from math import inf
from time import time
from pftp.proto.checksum import verify, checksum
from pftp.proto.header import PFTPHeader as Header
from pftp.proto.sequence import SequenceNumberGenerator
from pftp.proto.pftpsocket import PFTPSocket, SendError, ReceiveError
from pftp.proto.segment import PFTPSegment as Segment, SegmentBuilder, MalformedSegmentError


class DuplicateSegmentError(Exception):
    pass

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
        return True if self.err_prob >= random.uniform(0.0, 1.0) else False

    def close(self):
        self.sock.close()

    def rdt_recv(self, timeout=inf):
        """ starts the server """

        def stopped(t):
            return True if t <= 0 else False
        
        seq_gen = SequenceNumberGenerator()
        while not stopped(timeout):
            start_time = time()
            _seq = Header.size() + self.mss
            try:
                current_seq, current_seq_bytes = seq_gen.get_next(_seq)
                self.logger.info('Receiving {} bytes of data'.format(self.mss + Header.size()))
                data, addr = self.udt_recv(size=self.mss + Header.size())

                segment = SegmentBuilder.from_bytes(data)

                # checksum
                if not verify(segment):
                    self.logger.info('Checksum failed')
                    raise MalformedSegmentError 

                # simulate error
                if self._errored():
                    self.logger.info('Simulating error')
                    raise MalformedSegmentError
                
                to_ack, to_yield = current_seq_bytes, segment.data
                if current_seq > int(segment.header.seq, 2):
                    to_ack, to_yield = segment.header.seq, b''
                    seq_gen.undo(_seq)

                ack = SegmentBuilder().with_data(b'').with_seq(to_ack).with_type(Segment.TYPE_ACK).build()

                self.udt_send(data=ack.to_bytes(), dest=addr)

                # deliver data to upper layer
                yield to_yield
            except (MalformedSegmentError, SendError, ReceiveError):
                seq_gen.undo(_seq)
                self.logger.info('Retrying segment with seq {}'.format(seq_gen.get_current()[0]))
            except Exception as e:
                self.logger.info('Unexpected error in server {}'.format(str(e)))
            except:
                self.logger.info('Unknown error in server')
            finally:
                timeout -= time() - start_time
        else:
            yield b''
