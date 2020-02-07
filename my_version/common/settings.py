"""Параметры работы серверного и клиентского скриптов"""

import logging

# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_QUEUE_SIZE = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# время лблокировки сокета клиентом
SOCKET_TIMEOUT = 0.2
# таймаут для системного вызова select
SELECT_WAIT = 0
# Кодировка проекта
ENCODING_TYPE = 'utf-8'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
# USER = 'user'
MSG_SOURCE = 'from_user'
MSG_DESTINATION = 'to_user'
ACCOUNT_NAME = 'account_name'

# Ключи типа ACTION
PRESENCE = 'presence'
PROBE = 'probe'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
# Отключение от сервера
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'


# Прочие ключи
RESPONSE = 'response'
ERROR = 'error'

# Уровень логирования
SERV_LOGGING_LEVEL = logging.DEBUG
CLIENT_LOGGING_LEVEL = logging.DEBUG


# Ответы сервера
# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}