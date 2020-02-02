"""сервер, отправляющий эхо-ответ клиентам. клиенты подключаются к сокету сервера по очереди,
время блокировки сокета 0.2 секунды/клиент
запросы от всех клиентов обрабатываются по очереди"""

import select
from socket import socket, AF_INET, SOCK_STREAM

ADDRESS = ('localhost', 8000)


def read_message(read_client, all_clients):
    """чтение запросов от клиентов"""
    requests = {}

    for sock in read_client:
        try:
            data = sock.recv(1024).decode('utf-8')
            requests[sock] = data
        except Exception:
            print(f'клиент {sock.getpeername()} отключился')
            all_clients.remove(socket)
    return requests


def write_message(requests, write_client, all_clients):
    """ответ клиентам"""

    for sock in write_client:
        # если клиент есть в списке и он отправлял сообщение серверу
        if sock in requests:
            try:
                response = requests[sock].upper()
                sock.send(response.encode('utf-8'))
            except Exception:
                print(f'клиент {sock.getpeername()} отключился')
                sock.close()
                all_clients.remove(sock)


def main(addr):
    """Основная функция, обрабатывающая запросы клиентов"""

    all_clients = []

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind(addr)
        s.listen(5)
        s.settimeout(0.1)
        while True:
            try:
                cl_sock, cl_addr = s.accept()
            except OSError:
                pass
            else:
                print(f"получен запрос на соединение от клиента {cl_sock.getpeername()}")
                all_clients.append(cl_sock)
            finally:
                clients_read = []
                clients_write = []
                try:
                    clients_read, clients_write, err = select.select(all_clients, all_clients, [], 0)
                except Exception:
                    pass

                requests = read_message(clients_read, all_clients)
                if requests:
                    print(requests)
                if requests:
                    write_message(requests, clients_write, all_clients)


print("Запускаю эхо-сервер... ")
main(ADDRESS)
