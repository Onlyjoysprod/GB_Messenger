from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
import json
import argparse
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_SERVER_IP_ADDRESS, DEFAULT_PORT, MAX_CONNECTIONS, DESTINATION, SENDER, RESPONSE_200, RESPONSE_400, \
    MESSAGE, MESSAGE_TEXT, EXIT
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


# def write_responses(messages, w_clients, all_clients):
#     for sock in w_clients:
#         for message in messages:
#             try:
#                 response = process_client_message(message)
#                 send_message(sock, response)
#             except:
#                 print(f'Client {sock.fileno()} {sock.getpeername()} disconnected')
#                 sock.close()
#                 all_clients.remove(sock)

@log
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        server_log.info(f'Send message to user {message[DESTINATION]} '
                        f'from {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        server_log.error(
            f'User {message[DESTINATION]} not registered, '
            f'cant send message to wrong user.')


@log
def process_client_message(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, отправляет словарь-ответ в случае необходимости.
    :param message:
    :param messages_list:
    :param client:
    :param clients:
    :param names:
    :return:
    """
    server_log.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and \
            TIME in message and USER in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Username not available'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь сообщений.
    # Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Иначе отдаём Bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Bad request'
        send_message(client, response)
        return


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
    transport.settimeout(0.5)

    clients = []
    messages = []
    names = dict()

    transport.listen(MAX_CONNECTIONS)
    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            server_log.info(f'Connected with {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    server_log.info(f'Client {client_with_message.getpeername()} '
                                    f'was disconnected.')
                    clients.remove(client_with_message)

        # Если есть сообщения, обрабатываем каждое.
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                server_log.info(f'Connection with {i[DESTINATION]} was lost')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()

    # while True:
    #     try:
    #         client, client_address = transport.accept()
    #         server_log.info(f'Connected client: {client_address}')
    #     except OSError as err:
    #         pass
    #     else:
    #         clients.append(client)
    #     finally:
    #         wait = 0
    #         r = []
    #         w = []
    #         try:
    #             r, w, e = select.select(clients, clients, [], wait)
    #         except:
    #             pass
    #
    #         requests = read_requests(r, clients)
    #         if requests:
    #             process_message(requests, w, clients)


if __name__ == '__main__':
    main()
