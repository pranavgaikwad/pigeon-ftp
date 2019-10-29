from pftp.client.pftpclient import PFTPClient

if __name__ == "__main__":
    msg = lambda x: b'10' * (x // 2)
    msg_size = int(input('Enter Message Size: '))
    mss = int(input('Enter MSS: '))
    atimeout = float(input('Enter Wait Timeout: '))  # 0.03 seconds is the sweet spot is servers are on same machine
    no_clients = int(input('Enter No of Receivers: '))
    timeout = int(input('Enter Stop Timeout: '))

    print('Enter Receiver <Host>,<Port> each on new line...')

    addresses = []
    for i in range(no_clients):
        x = input()
        addresses.append((str(x).split(',')[0], int(str(x).split(',')[1])))

    input('Press Enter to start transmitting file')

    PFTPClient(addresses, atimeout=atimeout, mss=mss).rdt_send(msg(msg_size), btimeout=timeout)
