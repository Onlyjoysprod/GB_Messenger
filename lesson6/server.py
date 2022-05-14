from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
import json
import argparse
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_SERVER_IP_ADDRESS, DEFAULT_PORT, MAX_CONNECTIONS
from common.utils import get_message, send_message, log
from log.server_log_config import server_log

parser = argparse.ArgumentParser(description='address and port')
parser.add_argument('-a', dest="addr", default=DEFAULT_SERVER_IP_ADDRESS)
parser.add_argument('-p', dest="port", default=DEFAULT_PORT)
args = parser.parse_args()


@log
def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


@log
def main():
    try:
        listen_port = int(args.port)
        listen_address = args.addr
        if listen_port < 1024 or listen_port > 65535:
            server_log.error('Port can be in range 1024-6535')
            raise ValueError
    except ValueError:
        sys.exit(1)

    transport = socket(AF_INET, SOCK_STREAM)
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        server_log.info(f'Connected client: {client_address}')
        try:
            message_from_client = get_message(client)
            server_log.info(f'Get message from client: {message_from_client}')
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            server_log.info(f'Send response to client: {response}')
            client.close()
        except (ValueError, json.JSONDecodeError):
            server_log.error('Got incorrect message from client')
            client.close()


if __name__ == '__main__':
    main()
