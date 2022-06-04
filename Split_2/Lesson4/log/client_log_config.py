import os
import logging

client_log = logging.getLogger('client')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

file_hand = logging.FileHandler(PATH, encoding='utf-8')
file_hand.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)-10s %(asctime)s %(message)s")

file_hand.setFormatter(formatter)

client_log.addHandler(file_hand)
client_log.setLevel(logging.DEBUG)
