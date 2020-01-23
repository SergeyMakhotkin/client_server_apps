"""Клиентская часть"""

from sys import argv, exit
from json import JSONDecodeError
import socket
import time
from my_package.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from my_package.common_functions import get_message, send_message


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
    return msg


def process_server_ans(message):
    '''
    Обработка кодов ответа от сервера
    :param message:
    :return:
    '''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
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
    try:
        serv_addr = argv[1]
        serv_port = int(argv[2])
        if not (1024 <= serv_port <= 65535):
            raise ValueError
    except IndexError:
        serv_addr = DEFAULT_IP_ADDRESS
        serv_port = DEFAULT_PORT
    except ValueError:
        print("Вторым параметром должен быть указан порт (число в диапазоне 1024 - 65535")
        exit(1)

    # Создаем сокет, обмениваемся сообщениями с сервером

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((serv_addr, serv_port))
    message = generate_presence_msg()
    send_message(client_sock, message)
    try:
        answer = process_server_ans(get_message(client_sock))
        client_sock.close()
        print(answer)
    except (ValueError, JSONDecodeError):
        print('JSON decoding error.')


if __name__ == '__main__':
    main()
