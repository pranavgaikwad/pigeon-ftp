from pftp.client.pftpclient import PFTPClient

if __name__ == "__main__":
    msg = lambda x: b'10' * (x // 2)
    msg_size = int(input('Message size? '))
    mss = int(input('MSS? '))
    timeout = int(input('Timeout? '))
    no_clients = int(input('No of clients? '))
    print('Enter <host>,<port> each on new line...')
    addresses = []
    for i in range(no_clients):
        x = input()
        addresses.append((str(x).split(',')[0], int(str(x).split(',')[1])))

    input('Press enter to start')
    PFTPClient(addresses, atimeout=0.5, mss=mss).rdt_send(msg(msg_size), btimeout=timeout)
