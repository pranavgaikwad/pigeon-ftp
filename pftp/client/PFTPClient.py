from pftp.client.Client import Client


class PFTPClient(Client):
    """ Pigeon FTP client with SAW ARQ """

    def __init__(self, receivers, mss=4000, timeout=3000):
        """
        Args:
            receivers ([PFTPReceiver]): list of receivers
            mss (int, optional): maximum segment size. Defaults to 4000.
            timeout (int, optional): ARQ timeout in ms. Defaults to 3000.
        """
        self.receivers = {r: {} for r in receivers}

    def rdt_send(self, bytes, destination):
        return
