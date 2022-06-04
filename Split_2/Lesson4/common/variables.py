import logging

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

RESPONSE = 'response'
PRESENCE = 'presence'
MESSAGE = 'message'
SENDER = 'from'
DESTINATION = 'to'
MESSAGE_TEXT = 'mess_text'
ERROR = 'error'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

LOGGING_LEVEL = logging.DEBUG

DEFAULT_IP_ADDRESS = '127.0.0.1'
DEFAULT_SERVER_IP_ADDRESS = ''
DEFAULT_PORT = 7777

MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024

ENCODING = 'utf-8'

SERVER_DATABASE = 'sqlite:///server_base.db3'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO:None
                }
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
