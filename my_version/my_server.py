"""Серверная часть"""

import select
import socket
import argparse
import logging
from decorators import log
from json import JSONDecodeError
import log_config.server_log_config
from common.settings import ACTION, ACCOUNT_NAME, MAX_QUEUE_SIZE, PRESENCE, \
    TIME, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS, SOCKET_TIMEOUT, SELECT_WAIT, MESSAGE, MSG_SOURCE, \
    MSG_DESTINATION, MESSAGE_TEXT, QUIT, RESPONSE_200, RESPONSE_400
from common.common_functions import get_message, send_message, check_port_range

# Включаем логгирование
SERVER_LOG = logging.getLogger('app.server')


@log
def process_client_message(incoming_message, messages_list, client_sock, all_clients, users_dict):
    """
      Обработчик сообщений от клиента. Проверяет корректность формата сообщения.
    В качестве входящего сообщения принимает словарь. Отправляет ответ также в форме словаря
    В качестве кодов ответа использует коды HTTP.

    :param incoming_message:
    :param messages_list:
    :param client_sock:
    :param all_clients:
    :param users_dict:
    :return:
    """
    SERVER_LOG.debug(f'Обработка входящего сообщения от клиента: {incoming_message}')
    #  1. обработка сообщения типа PRESENCE
    if ACTION in incoming_message and incoming_message[ACTION] == PRESENCE and TIME in incoming_message \
            and MSG_SOURCE in incoming_message:
        SERVER_LOG.debug(f'принято сообщение от пользователя типа PRESENCE')
        # Проверяем, ести ли информация о пользователе отправителе, если нет, то добавляем в users_list
        if incoming_message[MSG_SOURCE][ACCOUNT_NAME] not in users_dict.keys():
            # добавляем пользователя в словарь. Ключ - его имя, значение - клиентский сокет
            users_dict[incoming_message[MSG_SOURCE][ACCOUNT_NAME]] = client_sock
            SERVER_LOG.info(f'Пользователь {incoming_message[MSG_SOURCE][ACCOUNT_NAME]} добавлен в список клиентов')
            send_message(client_sock, RESPONSE_200)
            SERVER_LOG.debug(f'Отправлен ответ от сервера {RESPONSE_200} клиенту {client_sock.getpeername()}')
        else:
            response = RESPONSE_400
            response[ERROR] = 'Указанное имя пользователя уже занято'
            send_message(client_sock, response)
            SERVER_LOG.error(f'пользователь {client_sock.getpeername()} указал username '
                             f'{incoming_message[MSG_SOURCE][ACCOUNT_NAME]}, который уже занят')
            all_clients.remove(client_sock)
            client_sock.close()
        return
    # 2. Если это сообщение от пользователя, добавляем его в список сообщений
    elif ACTION in incoming_message and incoming_message[ACTION] == MESSAGE and MSG_SOURCE in incoming_message \
            and MESSAGE_TEXT in incoming_message:
        messages_list.append(incoming_message)
        return
    # 3. Если это сообщение об отключении пользователя от сервера
    elif ACTION in incoming_message and incoming_message[ACTION] == QUIT and ACCOUNT_NAME in incoming_message:
        SERVER_LOG.info(f'Получено оповещение об отключении пользователя {incoming_message[MSG_SOURCE][ACCOUNT_NAME]}')
        all_clients.remove(users_dict[incoming_message[ACCOUNT_NAME]])
        # закрываем соединение с клиентом
        users_dict[incoming_message[ACCOUNT_NAME]].close()
        SERVER_LOG.debug(f'Соединение с пользователем {client_sock.getpeername()} завершено')
        del users_dict[incoming_message[ACCOUNT_NAME]]
        return
    # 4. Если сообщение не соответсвует ни одному из случаев
    else:
        response = RESPONSE_400
        response[ERROR] = "Некорректный запрос"
        send_message(client_sock, response)
        return


@log
def process_received_messages(message, users_dict, clients_write):
    """
    Функция отправки сообщения определенному адресату. Принимает на вход словарь-сообщение,
    словарь зарегистрированных пользователей и список сокетов клиентов, слушающих сервер.
    :param message:
    :param users_dict:
    :param clients_write:
    :return:
    """
    if message[MSG_DESTINATION] in users_dict and users_dict[message[MSG_DESTINATION]] in clients_write:
        send_message(users_dict[message[MSG_DESTINATION]], message)
        SERVER_LOG.info(f'Отправлено сообщение пользователю {users_dict[message[MSG_DESTINATION]]} '
                        f' от пользователя {message[MSG_SOURCE]}')
    elif message[MSG_DESTINATION] in users_dict and users_dict[message[MSG_DESTINATION]] not in clients_write:
        raise ConnectionError
    else:
        SERVER_LOG.error(
            f'Пользователь {message[MSG_DESTINATION]} на сервере не зарегистрирован, '
            f'отправка сообщения невозможна.')


def get_serv_args():
    """Создаем парсер для обработки параметров, переданных при запуске"""

    parser = argparse.ArgumentParser(description="server script")
    parser.add_argument(
        '--port',
        '-p',
        dest='port',
        type=check_port_range,
        metavar='INT',
        default=DEFAULT_PORT,
        nargs='?',
        help='listening port. allowed range 1024-65535')
    parser.add_argument(
        '--ip',
        '-a',
        dest='ip_addr',
        default=DEFAULT_IP_ADDRESS,
        nargs='?',
        help='allowed client ip addresses')
    args = parser.parse_args()
    SERVER_LOG.debug(f'При запуске переданы аргументы: {args}')
    return args


def main():
    """
    Проверка переданных параметров. Если отсутствуют - используются значения по умолчанию
    из файла settings.py
    Формат принимаемых параметров командной строки:
    server.py -p <port> -a <addr>
    :return:
    """

    # Аргументы запуска сервера
    serv_args = get_serv_args()
    # Список всех клиентов (список клиентских сокетов)
    all_clients_list = []
    # Список сообщений от клиентов, ожидающих отправки
    messages_list = []
    # Словарь, содержащий имена пользователей как ключи и сокеты пользователей как значение
    users_dict = dict()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((serv_args.ip_addr, serv_args.port))
        server_sock.settimeout(SOCKET_TIMEOUT)
        server_sock.listen(MAX_QUEUE_SIZE)
        SERVER_LOG.info(
            f'Запущен сервер, порт для подключений: {serv_args.port}, '
            f'адрес с которого принимаются подключения: {serv_args.ip_addr}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')

        # Основной цикл работы сервера
        while True:
            try:
                # проверяем, есть ли новые подключения (время ожидания подключения SOCKET_TIMEOUT)
                client_socket, client_address = server_sock.accept()
            except OSError:
                # нет входящих соединений
                pass
            else:
                all_clients_list.append(client_socket)
                SERVER_LOG.info(
                    f'Установлено соедение с Клиентом {client_address}')

            # Делаем проверку клиентских сокетов
            clients_ready_to_send_data = []
            clients_ready_to_receive_data = []
            try:
                clients_ready_to_send_data, clients_ready_to_receive_data, _ = select.select(
                    all_clients_list, all_clients_list, [], SELECT_WAIT)
            except OSError:
                # нет установленных соединений с клиентами
                pass

            # если есть клиенты, готовые передать сообщение - принимаем
            if clients_ready_to_send_data:
                for client in clients_ready_to_send_data:
                    try:
                        process_client_message(get_message(client), messages_list, client, all_clients_list, users_dict)
                    except Exception:
                        SERVER_LOG.info(f'Клиент {client.getpeername()} отключился от сервера')
                        all_clients_list.remove(client)

            # если есть неотправленные сообщения - обрабатываем их
            # сообщения, которые не удается отправить удаляются из очереди
            for m in messages_list:
                try:
                    process_received_messages(m, users_dict, clients_ready_to_receive_data)
                except Exception:
                    SERVER_LOG.info(f'Связь с клиентом {m[MSG_DESTINATION]} потеряна. сообщение не отправлено')
                    print('users_dict', users_dict)
                    print('all_clients_list', all_clients_list)
                    try:
                        all_clients_list.remove(users_dict[m[MSG_DESTINATION]])
                        SERVER_LOG.debug(f'Пользователь {users_dict[m[MSG_DESTINATION]]} '
                                         f'удален из списка пользователей')
                    except Exception:
                        SERVER_LOG.debug('не удалось удалить пользователя из списка. возможно, он был удален ранее')
                    try:
                        del users_dict[m[MSG_DESTINATION]]
                        SERVER_LOG.debug(
                            f'имя {users_dict[m[MSG_DESTINATION]]} удалено из списка имен')
                    except Exception:
                        SERVER_LOG.debug('не удалось удалить имя пользователя из списка имен. '
                                         'возможно, оно было удалено ранее')
                messages_list.clear()


if __name__ == '__main__':
    main()
