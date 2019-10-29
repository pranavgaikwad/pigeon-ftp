import sys
from time import time

from pftp.client.pftpclient import PFTPClient

if __name__ == "__main__":
    n = 3
    MSS = 500
    server_port = 7735
    atimeout = 0.05

    servers = [('152.46.19.167', server_port),
               ('152.46.19.168', server_port),
               ('152.46.19.169', server_port),
               ('192.168.10.62', server_port),
               ('192.168.10.172', server_port)]

    with open('data.txt', 'rb') as file:
        data = file.read()

    input('Press Enter to start P2MPClient with n: {}, MSS: {}, atimeout: {}'.format(n, MSS, atimeout))

    start = time()
    sent = PFTPClient(servers[:n], mss=MSS, atimeout=atimeout).rdt_send(data)

    print('SENT {} bytes'.format(sent))
    print('TIME TAKEN {:.2f} seconds'.format(time() - start))
