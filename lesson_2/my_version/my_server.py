"""Серверная часть"""

import socket
import argparse
import logging
from decorators import log
from json import JSONDecodeError
import log_config.server_log_config
from common.settings import ACTION, ACCOUNT_NAME, RESPONSE, MAX_QUEUE_SIZE, PRESENCE, \
    TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS
from common.common_functions import get_message, send_message, check_port_range



# Включаем логгирование
SERVER_LOG = logging.getLogger('app.server')

@log
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
        RESPONSE: 400,
        ERROR: 'Bad Request'
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
    SERVER_LOG.debug(f'При запуске переданы аргументы: {args}')

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((args.ip_addr, args.port))
    SERVER_LOG.info(
        f'Запущен сервер, порт для подключений: {args.port}, '
        f'адрес с которого принимаются подключения: {args.ip_addr}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')
    server_sock.listen(MAX_QUEUE_SIZE)

    while True:
        client_socket, client_address = server_sock.accept()
        SERVER_LOG.info(f'Установлено соедение с Клиентом {client_address}')
        try:
            message_from_client = get_message(client_socket)
            SERVER_LOG.debug(
                f'От клиента {client_address} получено сообщение: {message_from_client}')
            response = process_client_message(message_from_client)
            SERVER_LOG.info(f'Cформирован ответ клиенту "{response}"')
            send_message(client_socket, response)
            SERVER_LOG.info(
                f'Клиенту {client_address} отправлено сообщение "{response}"')
            client_socket.close()
            SERVER_LOG.info(
                f'Соединение c клиентом {client_address} закрывается')
        except (ValueError, JSONDecodeError):
            print('Некорректный формат сообщения от клиента.')
            SERVER_LOG.error(
                f'Не удалось декодировать Json строку, полученную от '
                f'клиента {client_address}. Соединение закрывается.')
            client_socket.close()


if __name__ == '__main__':
    main()
