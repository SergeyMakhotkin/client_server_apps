"""Клиентская часть"""

import argparse
import socket
import time
import logging
import threading
import log_config.client_log_config
from sys import exit
from json import JSONDecodeError
from decorators import log
from common.settings import ACTION, PRESENCE, TIME, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MSG_SOURCE, \
    MSG_DESTINATION, MESSAGE_TEXT, QUIT
from common.common_functions import get_message, send_message
from error_exceptions import IncorrectDataReceivedError, ReqFieldMissingError, ServerError

# Включаем логгирование
CLIENT_LOG = logging.getLogger('app.client')


def print_help():
    """Вывод справки по использованию клиента"""
    print('Поддерживаемые команды: \n'
          '1. message - отправить сообщение. Кому и текст будет запрошены отдельно. \n'
          '2. help - вывести подсказки по командам \n'
          '3. exit - выход из программы \n')


@log
def generate_presence_msg(account_name='Guest'):
    """
    Создание сообщения типа "PRESENCE"
    :param account_name:
    :return:
    """
    msg = {
        ACTION: PRESENCE,
        TIME: time.ctime(),
        MSG_SOURCE: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOG.debug(
        f'Сформировано {PRESENCE} сообщение от пользователя {account_name}')
    return msg


@log
def get_message_from_server(sock, my_username):
    """
    Оброботчик сообщений от сервера, адресованных текущему пользователю

    :param sock:
    :param my_username:
    :return:
    """
    while True:
        try:
            message = get_message(sock)
            # Делаем проверку полученного сообщения
            if ACTION in message and message[ACTION] == MESSAGE and MSG_SOURCE in message \
                    and MSG_DESTINATION in message and message[MSG_DESTINATION] == my_username:
                print(f'Сообщение от пользователя {message[MSG_SOURCE]}: '
                      f'{message[MESSAGE_TEXT]}')
                CLIENT_LOG.info(f'Получено сообщение от пользователя {message[MSG_SOURCE]}')
                CLIENT_LOG.debug(f'{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOG.error(f'Получено сообщение некорректного формата либо для другого адресата')
                CLIENT_LOG.debug(f'{message}')
        except (IncorrectDataReceivedError, JSONDecodeError):
            CLIENT_LOG.error(f'Не удалось декодировать принятое сообщение')
        except (OSError, ConnectionAbortedError, ConnectionError, ConnectionResetError):
            CLIENT_LOG.critical('Потяряно соеднение с сервером')
            break


@log
def create_message_to_user(sock, account_name='Guest'):
    """
    Функция запрашивает текст сообщения и имя пользователя. Формирует словарь заданного формата,
    отправляет данные на сервер

    :param sock:
    :param account_name:
    :return:
    """
    destination = input('Введите получателя сообщения: ')
    message = input('Введите текст сообщения: \n')
    m_dict = {
        ACTION: MESSAGE,
        MSG_SOURCE: account_name,
        MSG_DESTINATION: destination,
        TIME: time.ctime(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOG.info(f'Сформировано сообщение для отправки пользователю {destination}')
    CLIENT_LOG.debug(f'{m_dict}')
    try:
        send_message(sock, m_dict)
        CLIENT_LOG.info(f'сообщение для пользователя {destination} отправлено на сервер')
    except:
        CLIENT_LOG.critical('Потяряно соеднение с сервером')
        exit(1)


@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: QUIT,
        TIME: time.ctime(),
        ACCOUNT_NAME: account_name
    }


@log
def user_cli_commands(sock, username):
    """Взаимодействие пользователя с программой-клиентом"""
    print_help()
    while True:
        command = input('Введите команду или ее номер: ')
        if command in ('message', '1'):
            create_message_to_user(sock, username)
        elif command in ('help', '2'):
            print_help()
        elif command in ('exit', '3'):
            send_message(sock, create_exit_message(username))
            print('Отключение от сервера...')
            CLIENT_LOG.info('Пользователь завершил соединение')
            time.sleep(0.5)
            break
        else:
            print('Неизвестная комманда. Для вызова справки введите help')


@log
def msg_to_chat(message_to_send, account_name='Guest'):
    """
    Отправка сообщения в чат
    """
    msg = {
        ACTION: MESSAGE,
        TIME: time.ctime(),
        MSG_SOURCE: {
            ACCOUNT_NAME: account_name
        },
        MESSAGE: message_to_send
    }
    # CLIENT_LOG.debug(
    #     f'Сформировано {MSG} сообщение от пользователя {account_name}')
    return msg


@log
def process_server_response(message):
    """
    Обработка кодов ответа от сервера
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOG.debug('От сервера получен ответ "200 : OK"')
            return '200 : OK'
        CLIENT_LOG.error(f'От сервера получен ответ "400 : {message[ERROR]}"')
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


def get_console_args():
    """"настройка получения аргументов из командной строки"""

    parser = argparse.ArgumentParser(description="Параметры запуска клиента")
    parser.add_argument(
        'ip',
        default=DEFAULT_IP_ADDRESS,
        nargs='?',
        help='server ip address')
    parser.add_argument(
        'port',
        default=DEFAULT_PORT,
        type=int,
        nargs='?',
        help='server tcp port. allowed range 1024-65535')
    parser.add_argument(
        '-n',
        '--name',
        dest='username',
        default=None,
        nargs='?',
        help='Имя пользователя')
    args = parser.parse_args()

    if not 1024 <= args.port <= 65535:
        CLIENT_LOG.critical(
            f'Введено некорректное значение TCP-порта ({args.port})'
            f'значение порта должно быть [1024 - 65535]')
        exit(1)

    server_ip = args.ip
    server_port = args.port
    client_username = args.username
    return server_ip, server_port, client_username


def main():
    """
    Проверка переданных параметров. Если отсутствуют - используются значения по умолчанию
    из файла settings.py
    Формат принимаемых параметров командной строки:
    client.py <addr> [<port>]
    """

    server_ip, server_port, client_username = get_console_args()
    print('Консольный месседжер. Клиент. \n', '#' * 30)

    # Запрашиваем имя пользователя, если оно не было указано при запуске программы
    if not client_username:
        client_username = input('Введите имя пользователя: ')
    CLIENT_LOG.info(f'Запущен клиент для пользователя {client_username}')
    print(f'Запущен клиент для пользователя {client_username}')
    print('=' * 30)

    # Создаем сокет, обмениваемся сообщениями с сервером

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((server_ip, server_port))
        message = generate_presence_msg(client_username)
        send_message(client_sock, message)
        server_answer = process_server_response(get_message(client_sock))
        CLIENT_LOG.info(f'Установлено соединение с сервером {server_ip} {server_port}. '
                        f'Ответ от сервера: {server_answer}')
        print('Соединение с сервером установлено.')
    except JSONDecodeError:
        CLIENT_LOG.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        CLIENT_LOG.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOG.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOG.critical(
            f'Не удалось подключиться к серверу {server_ip}:{server_port}, '
            f'Сервер отклонил запрос на подключение.')
        exit(1)
    else:
        # Если все нормально
        # Запускаем прием сообщений в отдельном потоке
        receiver = threading.Thread(target=get_message_from_server, args=(client_sock, client_username), daemon=True)
        receiver.start()
        CLIENT_LOG.debug(f'Запущен поток id:{receiver.ident} приема сообщений пользователя.')

        # Запускаем поток ввода команд и отправки сообщений
        user_cli = threading.Thread(target=user_cli_commands, args=(client_sock, client_username), daemon=True)
        user_cli.start()
        CLIENT_LOG.debug(f'Запущен поток id:{user_cli.ident} интерфейса взаимодействия с пользователем.')

        # Проверяем запущенные потоки. Если один из них завершится - выходим из программы.
        while True:
            time.sleep(1)
            if not receiver.is_alive() or not user_cli.is_alive():
                break


if __name__ == '__main__':
    main()
