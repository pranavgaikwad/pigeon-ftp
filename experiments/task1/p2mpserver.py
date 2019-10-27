from pftp.server.pftpserver import PFTPServer
from pftp.utils.app_utils import get_true_ip
from sys import argv

if __name__ == "__main__":
    MSS = 500
    port = int(argv[1])
    p = float(argv[2])
    file = '{}:{}.txt'.format(get_true_ip(), port)

    input('Press Enter to start P2MPServer on port: {} with MSS: {}, p: {}'.format(port, MSS, p))

    addr = ('0.0.0.0', port)
    server = PFTPServer(addr=addr, mss=MSS, err_prob=p)

    with open(file, 'a+') as f:
        for data in server.rdt_recv():
            f.write(data.decode('utf-8'))

    server.close()
