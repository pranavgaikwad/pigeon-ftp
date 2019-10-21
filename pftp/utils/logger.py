import logging
import inspect
from threading import current_thread

def logger():
    _logger = logging.getLogger(__name__)
    if not _logger.hasHandlers():
        _logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s %(threadName)s %(asctime)-15s %(funcName)s %(message)s', '%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    return _logger
