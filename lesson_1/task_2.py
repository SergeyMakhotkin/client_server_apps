# Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
# кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

VAR_1 = b'class'
VAR_2 = b'function'
VAR_3 = b'method'
VAR_LIST = [VAR_1, VAR_2, VAR_3]

for i in VAR_LIST:
    print(f'{i}', type(i), len(i))
