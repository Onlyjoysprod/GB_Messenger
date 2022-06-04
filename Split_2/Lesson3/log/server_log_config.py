import os
import logging
from logging.handlers import TimedRotatingFileHandler

server_log = logging.getLogger('server')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

file_hand = TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
file_hand.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)-10s %(asctime)s %(message)s")

file_hand.setFormatter(formatter)

server_log.addHandler(file_hand)
server_log.setLevel(logging.DEBUG)
