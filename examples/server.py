from pftp.server.pftpserver import PFTPServer

if __name__ == "__main__":
    addr = ('127.0.0.1', int(input('Enter Port: ')))
    file = './{}'.format(input('Enter Filename: '))
    mss = int(input('Enter MSS: '))
    p = float(input('Enter Loss Probability P: '))
    timeout = int(input('Enter Server Timeout: '))

    input('Press Enter to start P2MPServer on port: {} with MSS: {}, p: {}'.format(addr[1], mss, p))

    server = PFTPServer(addr=addr, mss=mss, err_prob=p)

    with open(file, 'a+') as f:
        for data in server.rdt_recv(timeout=timeout):
            f.write(data.decode('utf-8'))

    server.close()
