import logging
import inspect

def logger():
    _logger = logging.getLogger(__name__)
    if not _logger.hasHandlers():
        _logger.setLevel(logging.INFO)
        func = inspect.currentframe().f_back.f_code
        formatter = logging.Formatter('%(levelname)s %(asctime)-15s %(funcName)s %(message)s', '%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    return _logger
