import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))
PFTPCLIENT_MEM_LIM = int(config.get('pftpclient', 'MEMORY_LIMIT'))