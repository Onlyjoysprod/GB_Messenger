import sys, json, time, argparse
import threading

from socket import socket, AF_INET, SOCK_STREAM

from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, EXIT
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, ServerError
from log.client_log_config import client_log
from decorator import log

from metaclasses import ClientVerifier


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()
        # проверка метакласса
        # s = socket()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        to_user = input('Enter destination user name: ')
        message = input('Enter your message: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        try:
            send_message(self.sock, message_dict)
            client_log.info(f'Sending message to user {to_user}')
        except Exception as e:
            print(e)
            client_log.critical('Lost connection with server.')
            sys.exit(1)

    def run(self):
        print('Commands: message, help, exit')
        while True:
            command = input('Your command: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                print('Commands: message, help, exit')
            elif command == 'exit':
                send_message(self.sock, self.create_exit_message())
                print('Connection end.')
                client_log.info('Program closed with user command')
                time.sleep(0.5)
                break
            else:
                print('Wrong command. Enter "help" to show commands')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            message = get_message(self.sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                print(f'\nMessage from user {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                client_log.info(f'Message from user {message[SENDER]}:'
                                f'\n{message[MESSAGE_TEXT]}')
            else:
                client_log.error(f'Wrong message from server: {message}')


@log
def create_presence(account_name):
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


@log
def arg_parser():
    parser = argparse.ArgumentParser(description='address and port')
    parser.add_argument('-a', dest="addr", default=DEFAULT_IP_ADDRESS)
    parser.add_argument('-p', dest="port", default=DEFAULT_PORT)
    parser.add_argument('-n', dest="name", default=None)
    args = parser.parse_args()

    server_address = args.addr
    server_port = int(args.port)
    client_name = args.name

    if server_port < 1024 or server_port > 65535:
        client_log.error('Port can be in range 1024-6535')
        sys.exit(1)

    return server_address, server_port, client_name


@log
def main():
    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Введите имя пользователя: ')
    print(f'client name {client_name}')
    client_log.info(f'Run client. Address: {server_address}, port: {server_port}, '
                    f'user name: {client_name}')

    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        client_log.info(f'Connected to port: {server_port}')
        message_to_server = create_presence(client_name)
        send_message(transport, message_to_server)
        client_log.info(f'Send message to server: {message_to_server}')
        answer = process_answer(get_message(transport))
        client_log.info(f'Server response: {answer}')
        print(answer)

    except json.JSONDecodeError:
        client_log.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        client_log.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        client_log.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        client_log.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        print('dgfsdghsdgsd')
        thread_read = ClientReader(client_name, transport)
        thread_read.daemon = True
        thread_read.start()

        thread_send = ClientSender(client_name, transport)
        thread_send.daemon = True
        thread_send.start()
        client_log.info('Run threads')

    while True:
        time.sleep(1)
        if thread_read.is_alive() and thread_send.is_alive():
            continue
        else:
            break


if __name__ == '__main__':
    main()
