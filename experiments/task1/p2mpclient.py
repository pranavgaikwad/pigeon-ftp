import sys
from time import time

from pftp.client.pftpclient import PFTPClient

if __name__ == "__main__":
    n = 3

    print('Starting P2MPClient Task 1 for n:', n)

    MSS = int(sys.argv[1])
    server_port = 7735
    atimeout = 0.05
    servers = [('152.46.19.48', 7741),
               ('152.46.19.48', 7742),
               ('152.46.19.48', 7743),
               ('152.46.19.48', 7738),
               ('152.46.19.48', 7739)]

    with open('../data.txt', 'rb') as file:
        data = file.read()

    input('Press Enter to start P2MPClient with n: {}, MSS: {}, atimeout: {}'.format(n, MSS, atimeout))

    start = time()
    sent = PFTPClient(servers[:n], mss=MSS, atimeout=atimeout).rdt_send(data)

    print('SENT {} bytes'.format(sent))
    print('TIME TAKEN', time() - start)
