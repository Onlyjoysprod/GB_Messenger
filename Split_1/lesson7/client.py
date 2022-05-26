import sys, json, time, argparse

from socket import socket, AF_INET, SOCK_STREAM

from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message
from log.client_log_config import client_log
from decorator import log

parser = argparse.ArgumentParser(description='address and port')
parser.add_argument('-a', dest="addr", default=DEFAULT_IP_ADDRESS)
parser.add_argument('-p', dest="port", default=DEFAULT_PORT)
parser.add_argument('-m', dest="mode", default='r')
args = parser.parse_args()


@log
def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


@log
def process_answer(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        else:
            return f'400: {message[ERROR]}'
    client_log.error('Wrong response')
    raise ValueError


def read_messages(client):
    while True:
        message = get_message(client)
        client_log.debug(f'Get message: {message}')
        print(message)


def write_messages(client):
    while True:
        message = create_presence()
        client_log.debug("Sending message...")
        send_message(client, message)


@log
def main():
    try:
        server_address = args.addr
        server_port = int(args.port)
        if server_port < 1024 or server_port > 65535:
            client_log.error('Port can be in range 1024-6535')
            raise ValueError
    except ValueError:
        sys.exit(1)

    try:
        mode = args.mode
        if not mode == 'r' or mode == 's':
            client_log.error('Wrong mode (can be r or s)')
            raise ValueError
    except ValueError:
        sys.exit(1)

    transport = socket(AF_INET, SOCK_STREAM)
    transport.connect((server_address, server_port))
    client_log.info(f'Connected to port: {server_port}')
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    client_log.info(f'Send message to server: {message_to_server}')

    try:
        answer = process_answer(get_message(transport))
        client_log.info(f'Server response: {answer}')
        print(answer)
        if answer == '200 : OK':
            if mode == 'r':
                read_messages(transport)
            elif mode == 's':
                write_messages(transport)
    except(ValueError, json.JSONDecodeError):
        client_log.warning('Can not decode message')


if __name__ == '__main__':
    main()
