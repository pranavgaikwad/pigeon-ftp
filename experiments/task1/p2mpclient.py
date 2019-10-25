import sys
from time import time
from csv import writer
from collections import defaultdict

from pftp.client.pftpclient import PFTPClient

if __name__ == "__main__":
    n = int(sys.argv[1])

    print('Starting P2MPClient Task 1 for n:', n)

    MSS = 500
    server_port = 7735
    servers = [('127.0.0.1', server_port), ('', server_port), ('', server_port), ('', server_port), ('', server_port)]

    with open('../data.txt', 'rb') as file:
        data = file.read()

    input('Press Enter to start')

    start = time()
    sent = PFTPClient(servers[:n], mss=MSS, atimeout=0.05).rdt_send(data)

    print('SENT', sent)
    print('TIME TAKEN', time() - start)
