"""функции, используемые и в серверном, и в клиентском скрипте"""

import json
from my_package.settings import MAX_PACKAGE_LENGTH, ENCODING_TYPE
import argparse


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
        return ValueError
    return ValueError


def send_message(socket, message):
    '''
    Утилита кодирования и отправки сообщения. В качестве аргументов принимает сокет
    и сообщение в виде словаря. Отправляет данные в байтовом закодированном виде
    :param socket:
    :param message:
    :return:
    '''

    if not isinstance(message, dict):
        raise TypeError
    json_message = json.dumps(message)
    encoded_json_message = json_message.encode(ENCODING_TYPE)
    socket.send(encoded_json_message)


def check_port_range(port_str):
    port_int = int(port_str)
    if port_int in range(1024, 65536):
        return port_int
    raise argparse.ArgumentTypeError(
        'Port number out of valid range 1024-65535')
