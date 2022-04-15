# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое
# программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию.
# Принудительно открыть файл в формате Unicode и вывести его содержимое.

from chardet import detect

f = open('test_file.txt', 'w', encoding='utf-8')
f. write('сетевое программирование\n'
         'сокет\n'
         'декоратор')
f.close()

with open('test_file.txt', 'rb') as f:
    content = f.read()
encoding = detect(content)['encoding']
print(f'encoding: {encoding}')

with open('test_file.txt', encoding=encoding) as f_n:
    for el_str in f_n:
        print(el_str, end='')
    print()
