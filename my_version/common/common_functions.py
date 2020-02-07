"""функции, используемые и в серверном, и в клиентском скрипте"""

import json
import argparse
import logging
import log_config.server_log_config
from common.settings import MAX_PACKAGE_LENGTH, ENCODING_TYPE
from error_exceptions import IncorrectDataReceivedError, NonDictInputError

SERV_LOGGER = logging.getLogger('app.server')


def get_message(client_socket):
    """функция для приема и декодирования сообщения из сокета.
    Принимает байты (если это не так - возвращает ошибку)
    Возвращает словарь
    :param client_socket
    :return:
    """

    encoded_data = client_socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_data, bytes):
        data = json.loads(encoded_data.decode(ENCODING_TYPE))
        if isinstance(data, dict):
            return data
        return IncorrectDataReceivedError
    return NonDictInputError


def send_message(socket, message):
    '''
    Утилита кодирования и отправки сообщения. В качестве аргументов принимает сокет
    и сообщение в виде словаря. Отправляет данные в байтовом закодированном виде
    :param socket:
    :param message:
    :return:
    '''

    if not isinstance(message, dict):
        raise NonDictInputError
    json_message = json.dumps(message)
    encoded_json_message = json_message.encode(ENCODING_TYPE)
    socket.send(encoded_json_message)


def check_port_range(port_str):
    port_int = int(port_str)
    if port_int in range(1024, 65536):
        return port_int
    SERV_LOGGER.critical(
        f'Попытка запуска сервера с указанием неподходящего порта '
        f'{port_str}. Допустимы адреса с 1024 до 65535.')
    raise argparse.ArgumentTypeError(
        'Port number out of valid range 1024-65535')
