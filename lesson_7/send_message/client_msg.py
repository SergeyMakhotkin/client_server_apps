"""клиент отправляющий и читающий сообщения"""

from socket import socket, AF_INET, SOCK_STREAM

serv_addr = ('localhost', 8000)

def echo(addr):
    """обмен сообщениями с сервером"""
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect(addr)
        while True:
            message = input("Введите сообщение: ")
            if message == 'exit':
                break
            sock.send(message.encode('utf-8'))
            data = sock.recv(1024).decode('utf-8')
            print(f"Сообщение от сервера: {data}")

if __name__ == '__main__':
    echo(serv_addr)