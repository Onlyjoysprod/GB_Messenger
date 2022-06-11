import socket
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../')
from common.utils import *
from common.variables import *
from errors import ServerError

from log.client_log_config import client_log

socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    # Сигналы новое сообщение и потеря соединения
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        # Класс База данных - работа с базой
        self.database = database
        # Имя пользователя
        self.username = username
        # Сокет для работы с сервером
        self.transport = None
        # Устанавливаем соединение:
        self.connection_init(port, ip_address)
        # Обновляем таблицы известных пользователей и контактов
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                client_log.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            client_log.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            client_log.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
            # Флаг продолжения работы транспорта.
        self.running = True

    def connection_init(self, port, ip):
        # Инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Таймаут необходим для освобождения сокета.
        self.transport.settimeout(5)

        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True если удалось
        connected = False
        for i in range(5):
            client_log.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        # Если соединится не удалось - исключение
        if not connected:
            client_log.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        client_log.debug('Установлено соединение с сервером')

        # Посылаем серверу приветственное сообщение и получаем ответ,
        # что всё нормально или ловим исключение.
        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.process_server_ans(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            client_log.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')

        # Если всё хорошо, сообщение об установке соединения.
        client_log.info('Соединение с сервером успешно установлено.')

    def create_presence(self):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        client_log.debug(f'Сформировано {PRESENCE} сообщение для пользователя {self.username}')
        return out

    def process_server_ans(self, message):
        client_log.debug(f'Разбор сообщения от сервера: {message}')

        # Если это подтверждение чего-либо
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                client_log.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')

        # Если это сообщение от пользователя добавляем в базу, даём сигнал о новом сообщении
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and SENDER in message \
                and DESTINATION in message \
                and MESSAGE_TEXT in message \
                and message[DESTINATION] == self.username:
            client_log.debug(f'Получено сообщение от пользователя {message[SENDER]}:'
                         f'{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        client_log.debug(f'Запрос контакт листа для пользователя {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        client_log.debug(f'Сформирован запрос {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        client_log.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            client_log.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        client_log.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            client_log.error('Не удалось обновить список известных пользователей.')

    def add_contact(self, contact):
        client_log.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def remove_contact(self, contact):
        client_log.debug(f'Удаление контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        client_log.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def send_message(self, to, message):
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        client_log.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            client_log.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        client_log.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет. Если не сделать тут задержку,
            # то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        # выход по таймауту вернёт номер ошибки err.errno равный None
                        # поэтому, при выходе по таймауту мы сюда попросту не попадём
                        client_log.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    client_log.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    client_log.debug(f'Принято сообщение с сервера: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)
