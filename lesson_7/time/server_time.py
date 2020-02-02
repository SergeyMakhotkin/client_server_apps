"""Сервер, который будет отправлять подключенным клиентам время"""

import time
import select
from socket import socket, AF_INET, SOCK_STREAM


def start_listen_socket(addr_port):
    """
    Инициализация серверного сокета
    :param addr_port:
    :return:
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(addr_port)
    sock.listen(5)
    sock.settimeout(1)
    return sock


def main():
    """основная функция программы"""
    address = ('localhost', 8888)
    all_client_list = []
    serv_sock = start_listen_socket(address)

    while True:
            try:
                # проверяем, есть ли новые подключения
                client_sock, addr = serv_sock.accept()
            except OSError:
                # ничего не делать, если клиент отключился
                print(f'нет новых подключений')
                pass
            else:
                # если все норм
                print(
                    f'новое соединение {client_sock.fileno()} {client_sock.getpeername()} {addr}')
                # добавляем новый сокет в список клиентов
                all_client_list.append(client_sock)
            finally:
                # создадим список клиентов, которым будем отправлять данные
                clients_wr = []
                try:
                    client_read, clients_wr, errors = select.select(
                        [], all_client_list, [], 0.2)
                except Exception:
                    print(f'нет клиентов, готовых к получению данных')

                for client in clients_wr:
                    time_str = time.ctime() + '\n'
                    try:
                        # если клиент не отключился отправляем время
                        client.send(time_str.encode('utf-8'))
                    except Exception:
                        # если клиент отключился - удаляем его из списка
                        print(f'клиент {client} отключился')
                        all_client_list.remove(client)


print("Сервер запущен")
main()
