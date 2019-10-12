from pftp.client.Client import Client

class PFTPClient(Client):
    """ Pigeon FTP client with SAW ARQ """

    def rdt_send(self, bytes, destination):
        return super().rdt_send(bytes, destination)
        
