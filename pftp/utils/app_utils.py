import logging
import socket


def logger():
    _logger = logging.getLogger(__name__)
    if not _logger.hasHandlers():
        _logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s %(threadName)s %(asctime)-15s %(funcName)s %(message)s',
                                      '%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    return _logger


def get_true_ip():
    """ returns address starting with '192.' """
    try:
        address = socket.gethostbyname(socket.gethostname())
    except:
        address = ''
    if not address or address.startswith('127.'):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.1', 0))
        address = s.getsockname()[0]
    return address
