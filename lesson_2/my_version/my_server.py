"""Серверная часть"""

import socket
import argparse
from json import JSONDecodeError
from my_package.settings import ACTION, ACCOUNT_NAME, RESPONSE, DEFAULT_QUEUE_SIZE, PRESENCE, \
    TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS, JSON_CHECK_FAULT
from my_package.common_functions import get_message, send_message, check_port_range


def process_client_message(message):
    """
    Обработчик сообщений от клиента. Проверяет корректность формата сообщения.
    Принимает словарь в качестве аргумента, возвращает словарь с ответом для клиента.
    В качестве кодов ответа использует коды HTTP.
    :param message:
    :return:
    """
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        JSON_CHECK_FAULT: 400,
        ERROR: 'Bad Request.'
    }


def main():
    """
    Проверка переданных параметров. Если отсутствуют - используются значения по умолчанию
    из файла settings.py
    Формат принимаемых параметров командной строки:
    server.py -p <port> -a <addr>
    :return:
    """

    # Создаем парсер для обработки параметров, переданных при запуске
    parser = argparse.ArgumentParser(description="server script")
    parser.add_argument(
        '--port',
        '-p',
        action='store',
        dest='port',
        type=check_port_range,
        metavar='INT',
        default=DEFAULT_PORT,
        help='listening port. allowed range 1024-65535')
    parser.add_argument(
        '--ip',
        '-a',
        action='store',
        dest='ip_addr',
        default=DEFAULT_IP_ADDRESS,
        help='allowed client ip addresses')
    args = parser.parse_args()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((args.ip_addr, args.port))
    server_sock.listen(DEFAULT_QUEUE_SIZE)

    while True:
        client_socket, client_address = server_sock.accept()
        try:
            message_from_client = get_message(client_socket)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client_socket, response)
            client_socket.close()
        except (ValueError, JSONDecodeError):
            print('Некорректный формат сообщения от клиента.')
            client_socket.close()


if __name__ == '__main__':
    main()
