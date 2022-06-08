import sys, json, time, argparse
import threading

from socket import socket, AF_INET, SOCK_STREAM

from common.variables import *
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from log.client_log_config import client_log
from decorator import log

from metaclasses import ClientVerifier
from client_database import ClientDatabase

sock_lock = threading.Lock()
database_lock = threading.Lock()


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
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

        with database_lock:
            if not self.database.check_user(to_user):
                client_log.error(f'Trying send message to user {to_user}')
                return

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }

        with database_lock:
            self.database.save_message(self.account_name, to_user, message)

        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                client_log.info(f'Message send to user {to_user}')
            except OSError as err:
                if err.errno:
                    client_log.critical('Lost connection')
                    exit(1)
                else:
                    client_log.error('Can not send message. Timeout')

    def run(self):
        print('Commands: message, help, exit')
        while True:
            command = input('Your command: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                print('Commands: message, help, exit')
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except Exception as e:
                        print(e)
                        pass
                    print('Connection closed.')
                time.sleep(0.5)
                break
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            elif command == 'edit':
                self.edit_contacts()

            elif command == 'history':
                self.print_history()

            else:
                print('Wrong command. Enter "help" to show commands')

    def print_history(self):
        ask = input('Show in messages - in, out messages - out, all messages - press Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nMessage from user: {message[0]} from {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nMessage to user: {message[1]} from {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nMessage from user: {message[0]} to user {message[1]} '
                          f'from {message[3]}\n{message[2]}')

    def edit_contacts(self):
        ans = input('enter "del" command for delete and "add" to add: ')
        if ans == 'del':
            edit = input('Enter name for delete: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    client_log.error('Cant delete this contact.')
        elif ans == 'add':
            edit = input('Enter name for add: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        client_log.error('Cant send to server.')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)

                except IncorrectDataRecivedError:
                    client_log.error(f'Can not decode message.')
                except OSError as err:
                    if err.errno:
                        client_log.critical(f'Lost connection.')
                        break
                except (ConnectionError,
                        ConnectionAbortedError,
                        ConnectionResetError,
                        json.JSONDecodeError):
                    client_log.critical(f'Lost connection with sercer.')
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE \
                            and SENDER in message \
                            and DESTINATION in message \
                            and MESSAGE_TEXT in message \
                            and message[DESTINATION] == self.account_name:
                        print(f'\n Received message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        # Захватываем работу с базой данных и сохраняем в неё сообщение
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER],
                                                           self.account_name,
                                                           message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                client_log.error('Database error')

                        client_log.info(f'Received message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        client_log.error(f'Received incorrect message: {message}')


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
def process_response_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


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


def contacts_list_request(sock, name):
    client_log.debug(f'Show contact list for user {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    client_log.debug(f'Request {req}')
    send_message(sock, req)
    ans = get_message(sock)
    client_log.debug(f'Response {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def add_contact(sock, username, contact):
    client_log.debug(f'Create contact {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Cant create contact')
    print('Contact created.')


def user_list_request(sock, username):
    client_log.debug(f'Request user list from {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def remove_contact(sock, username, contact):
    client_log.debug(f'Deleting contact {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Cant delete contact')
    print('Contact deleted')


def database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        client_log.error('User list error.')
    else:
        database.add_users(users_list)

    # Загружаем список контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        client_log.error('Contact list error.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


@log
def main():
    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Client run with name: {client_name}')
    print(f'client name {client_name}')
    client_log.info(f'Run client. Address: {server_address}, port: {server_port}, '
                    f'user name: {client_name}')

    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.settimeout(1)

        transport.connect((server_address, server_port))
        client_log.info(f'Connected to port: {server_port}')
        message_to_server = create_presence(client_name)
        send_message(transport, message_to_server)
        client_log.info(f'Send message to server: {message_to_server}')
        answer = process_response_ans(get_message(transport))
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
        database = ClientDatabase(client_name)
        database_load(transport, database, client_name)

        thread_read = ClientReader(client_name, transport, database)
        thread_read.daemon = True
        thread_read.start()

        thread_send = ClientSender(client_name, transport, database)
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
