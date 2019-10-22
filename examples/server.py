from pftp.server.pftpserver import PFTPServer

if __name__ == "__main__":
    addr = ('127.0.0.1', int(input('Port? ')))
    file = './{}'.format(input('Filename? '))
    server = PFTPServer(addr=addr, mss=4000, err_prob=0.0)
    timeout = int(input('Timeout? '))
    input('Press enter to start')
    with open(file, 'a+') as f:
        for data in server.rdt_recv(timeout=timeout):
            f.write(data.decode('utf-8'))
    server.close()