import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from log.client_log_config import client_log
from functools import wraps
import inspect


def decode_to_dict(byte_message):
    try:
        if isinstance(byte_message, bytes):
            dict_message = byte_message.decode(ENCODING)
            message = json.loads(dict_message)
            return message
        else:
            raise TypeError
    except TypeError:
        print('Неверный тип данных')


def encode_to_bytes(dict_message):
    try:
        if isinstance(dict_message, dict):
            json_message = json.dumps(dict_message)
            byte_message = json_message.encode(ENCODING)
            return byte_message
        else:
            raise TypeError
    except TypeError:
        print('Неверный тип данных')


def get_message(client):
    bresponse = client.recv(MAX_PACKAGE_LENGTH)
    response = decode_to_dict(bresponse)
    return response


def send_message(sock, message):
    bpresence = encode_to_bytes(message)
    sock.send(bpresence)


def log(func):
    @wraps(func)
    def call_info(*args, **kwargs):
        res = func(*args, **kwargs)
        client_log.debug(f'Function {func.__name__} was called from {inspect.stack()[1][3]}')
        client_log.debug(f'Function {func.__name__}({args}, {kwargs}), return {res}')
        return res
    return call_info
