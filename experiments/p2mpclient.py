import sys
from time import time

from pftp.client.pftpclient import PFTPClient

if __name__ == "__main__":
    n = int(sys.argv[1])
    MSS = int(sys.argv[2])
    atimeout = float(sys.argv[3])
    server_port = 7735

    servers = [('152.46.19.167', server_port),
               ('152.46.19.168', server_port),
               ('152.46.19.169', server_port),
               ('192.168.10.62', server_port),
               ('192.168.10.172', server_port)]

    with open('data.txt', 'rb') as file:
        data = file.read()

    input('Press Enter to start P2MPClient with n: {}, MSS: {}, Wait Timeout: {}'.format(n, MSS, atimeout))

    start = time()
    sent = PFTPClient(servers[:n], mss=MSS, atimeout=atimeout).rdt_send(data)

    print('Took {:.2f} seconds to sent {} bytes'.format(time() - start, sent))
