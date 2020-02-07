# Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

VAR_1 = 'attribute'
VAR_2 = 'класс'
VAR_3 = 'функция'
VAR_4 = 'type'

VAR_LIST = [VAR_1, VAR_2, VAR_3, VAR_4]
result = []
for item in VAR_LIST:
    try:
        # print( f"b'{item}'")
        # print(bytes(item, encoding='utf-8'))
        print(exec(f'b{item}'))
    except Exception as e:
        print(e.__class__)



