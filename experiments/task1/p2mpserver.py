from pftp.server.pftpserver import PFTPServer
from pftp.utils.app_utils import get_true_ip

if __name__ == "__main__":
    MSS = 500
    p = 0.05
    port = 7735
    file = '{}:{}.txt'.format(get_true_ip(), port)

    addr = ('0.0.0.0', port)
    server = PFTPServer(addr=addr, mss=MSS, err_prob=p)

    input('Press Enter to start')

    with open(file, 'a+') as f:
        for data in server.rdt_recv():
            f.write(data.decode('utf-8'))

    server.close()
