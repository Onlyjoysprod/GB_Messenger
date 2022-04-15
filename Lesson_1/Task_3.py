# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в
# байтовом типе.

words = ['attribute', 'класс', 'функция', 'type']


for word in words:
    try:
        word_enc = word.encode(encoding='ascii')
        print(f'{word_enc}, тип: {type(word_enc)}')
    except Exception as e:
        print(f'ERROR: {e}')
        print(f'слово {word} невозможно записать в байтовом типе')
