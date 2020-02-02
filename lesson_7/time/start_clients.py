"""Скрипт запуска нескольких клиентских приложений"""

from subprocess import Popen, CREATE_NEW_CONSOLE

# будем хранить информацию о запущенных процессах в списке
PROCESS_LIST = []

while True:
    console_input = input("для запуска 5 клиентов введите (s)"
                          "для закрытия клиентов введите (x)"
                          "для выхода введите (q)")
    # действия в зависимости от ввода параметра в консоль:
    if console_input == 'q':
        break
    elif console_input == 's':
        for _ in range(5):
            process = Popen('python time_client.py', creationflags=CREATE_NEW_CONSOLE)
            print(process)
            PROCESS_LIST.append(process)
        print('Запущено 5 клиентов time_client.py')
    elif console_input == 'x':
        for pr in PROCESS_LIST:
            pr.kill()
        PROCESS_LIST.clear()