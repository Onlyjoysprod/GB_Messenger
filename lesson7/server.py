from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
import json
import argparse
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_SERVER_IP_ADDRESS, DEFAULT_PORT, MAX_CONNECTIONS
from common.utils import get_message, send_message
from log.server_log_config import server_log
from decorator import log

import select

parser = argparse.ArgumentParser(description='address and port')
parser.add_argument('-a', dest="addr", default=DEFAULT_SERVER_IP_ADDRESS)
parser.add_argument('-p', dest="port", default=DEFAULT_PORT)
args = parser.parse_args()


def read_requests(r_clients, all_clients):
    messages = []
    for sock in r_clients:
        try:
            message = get_message(sock)
            messages.append(message)
        except:
            print(f'Client {sock.fileno()} {sock.getpeername()} disconnected')
            all_clients.remove(sock)

    return messages


def write_responses(messages, w_clients, all_clients):
    for sock in w_clients:
        for message in messages:
            try:
                response = process_client_message(message)
                send_message(sock, response)
            except:
                print(f'Client {sock.fileno()} {sock.getpeername()} disconnected')
                sock.close()
                all_clients.remove(sock)


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
    global transport
    global client
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
    transport.settimeout(0.2)
    clients = []

    while True:
        try:
            client, client_address = transport.accept()
            server_log.info(f'Connected client: {client_address}')
        except OSError as err:
            pass
        else:
            clients.append(client)
        finally:
            wait = 0
            r = []
            w = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except:
                pass

            requests = read_requests(r, clients)
            if requests:
                write_responses(requests, w, clients)


if __name__ == '__main__':
    main()
