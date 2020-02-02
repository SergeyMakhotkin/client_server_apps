"""клиент, получающий данные от сервера"""

from socket import socket, AF_INET, SOCK_STREAM

# Открываем сокет для соединения с сервером
with socket(AF_INET, SOCK_STREAM) as SOCKET:
    SOCKET.connect(('localhost', 8888))

    # данные от сервера будем получать бесконечно
    while True:
        print(f'Текущее время: {SOCKET.recv(1024).decode(encoding="utf-8")}')

