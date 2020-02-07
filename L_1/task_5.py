'''Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.'''


import subprocess
import chardet



COMMAND_1 = ['ping', 'ya.ru']
COMMAND_2 = ['ping', 'youtube.com']
COMMAND_LIST = [COMMAND_1, COMMAND_2]
ping_process = subprocess.Popen(COMMAND_LIST[0], stdout=subprocess.PIPE)
for line in ping_process.stdout:
    info = chardet.detect(line)
    line = line.decode(info['encoding']).encode('utf-8')
    print(line.decode('utf-8'))


