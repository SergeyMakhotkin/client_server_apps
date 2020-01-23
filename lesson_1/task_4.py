# Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового
# представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).

VAR_1 = 'разработка'
VAR_2 = 'администрирование'
VAR_3 = 'protocol'
VAR_4 = 'standard'

VAR_LIST = [VAR_1, VAR_2, VAR_3, VAR_4]
for item in VAR_LIST:
    utf_code = bytes(item, 'utf-8')
    print(f'{item}', utf_code, utf_code.decode('utf-8'), sep='\n')
    print('*' * 50)
