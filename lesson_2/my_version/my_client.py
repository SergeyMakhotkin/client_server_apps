"""Клиентская часть"""

from sys import exit
from json import JSONDecodeError
import socket
import argparse
import time
import logging
import log_config.client_log_config
from decorators import log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.common_functions import get_message, send_message

# Включаем логгирование
CLIENT_LOG = logging.getLogger('app.client')


@log
def generate_presence_msg(account_name='Guest'):
    '''
    Создание сообщения типа "PRESENCE"
    :param account_name:
    :return:
    '''
    msg = {
        ACTION: PRESENCE,
        TIME: time.ctime(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOG.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return msg


@log
def process_server_ans(message):
    '''
    Обработка кодов ответа от сервера
    :param message:
    :return:
    '''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOG.debug('От сервера получен ответ "200 : OK"')
            return '200 : OK'
        CLIENT_LOG.error(f'От сервера получен ответ "400 : {message[ERROR]}"')
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    """
    Проверка переданных параметров. Если отсутствуют - используются значения по умолчанию
    из файла settings.py
    Формат принимаемых параметров командной строки:
    client.py <addr> [<port>]
    """

    '''настройка получения аргументов из командной строки'''
    # try:
    #     serv_addr = argv[1]
    #     serv_port = int(argv[2])
    #     if not (1024 <= serv_port <= 65535):
    #         CLIENT_LOG.critical(f'Попытка запуска клиента с неподходящим номером порта: {serv_port}.'
    #                             f' Допустимы адреса с 1024 до 65535. Програбба закрывается.')
    #         raise ValueError
    # except IndexError:
    #     serv_addr = DEFAULT_IP_ADDRESS
    #     serv_port = DEFAULT_PORT
    #     CLIENT_LOG.info(f'Запущен клиент с парамертами: '
    #                     f'адрес сервера: {serv_addr} , порт: {serv_port}')
    # except ValueError:
    #     print("Вторым параметром должен быть указан порт (число в диапазоне 1024 - 65535")
    #     exit(1)

    parser = argparse.ArgumentParser(description="Параметры запуска клиентского скрипта")
    parser.add_argument('ip', default=DEFAULT_IP_ADDRESS, nargs='?', help='server ip address')
    parser.add_argument('port', default=DEFAULT_PORT, nargs='?', type=int, help='server tcp port')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        CLIENT_LOG.critical(f'Попытка запуска клиента с неподходящим номером порта: {args.port}.'
                            f' Допустимы адреса с 1024 до 65535. Програбба закрывается.')
        exit()

    CLIENT_LOG.info(f'Программа запущена с параметрами server_ip: {args.ip}, server_port: {args.port}')

    # Создаем сокет, обмениваемся сообщениями с сервером

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((args.ip, args.port))
    message = generate_presence_msg()
    send_message(client_sock, message)
    try:
        answer = process_server_ans(get_message(client_sock))
        CLIENT_LOG.info(f'Принят ответ от сервера {answer}')
        client_sock.close()
        CLIENT_LOG.debug(f'Соединение с сервером {args.ip}:{args.port} закрыто')
    except ConnectionRefusedError:
        CLIENT_LOG.debug(f'Не удалось подключиться к серверу {args.ip}:{args.port}, '
                         f'Соединение сброшено сервером.')
    except (ValueError, JSONDecodeError):
        CLIENT_LOG.error('Не удалось декодировать полученную Json строку.')


if __name__ == '__main__':
    main()
