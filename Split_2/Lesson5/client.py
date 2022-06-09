import sys, json, time, argparse
import threading

from socket import socket, AF_INET, SOCK_STREAM
from PyQt5.QtWidgets import QApplication

from common.variables import *
from errors import ServerError
from log.client_log_config import client_log
from decorator import log

from client.client_database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

sock_lock = threading.Lock()
database_lock = threading.Lock()

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


if __name__ == '__main__':
    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Создаём клиентокое приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке, то запросим его
    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект.
        # Иначе - выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    # Записываем логи
    client_log.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Создаём объект базы данных
    database = ClientDatabase(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    # Создаём GUI
    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
