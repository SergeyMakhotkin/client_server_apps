'''Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
 Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.'''


import chardet


STRINGS = ['сетевое программирование', 'сокет', 'декоратор']
with open('text_file.txt', 'w') as f:
    for line in STRINGS:
        f.write(line + '\n')

with open('text_file.txt', 'rb') as filedata:
    result = chardet.detect(filedata.read())
    char_enc = result['encoding']
    print(char_enc)



with open('text_file.txt', encoding=char_enc) as fn:
    for line in fn:
        print(line.strip())
