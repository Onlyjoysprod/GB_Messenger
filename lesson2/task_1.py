# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных
# данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV.

# Для этого: Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными,
# их открытие и считывание данных. В этой функции из считанных данных необходимо с помощью регулярных
# выражений извлечь значения параметров «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
# Значения каждого параметра поместить в соответствующий список. Должно получиться четыре списка — например,
# os_prod_list, os_name_list, os_code_list, os_type_list. В этой же функции создать главный список для хранения
# данных отчета — например, main_data — и поместить в него названия столбцов отчета в виде списка:
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
# Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);

# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
# В этой функции реализовать получение данных через вызов функции get_data(),
# а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv().

import csv
import re
import locale

default_encoding = locale.getpreferredencoding()
test_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data(file_list):
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    for file in file_list:
        with open(file, encoding=default_encoding) as f:
            for row in f:
                params = re.split(":\s+", row.strip())
                if type(params) == list and len(params) == 2:
                    if params[0] == headers[0]:
                        os_prod_list.append(params[1])
                    elif params[0] == headers[1]:
                        os_name_list.append(params[1])
                    elif params[0] == headers[2]:
                        os_code_list.append(params[1])
                    elif params[0] == headers[3]:
                        os_type_list.append(params[1])
    return headers, os_prod_list, os_name_list, os_code_list, os_type_list


def write_to_csv(file_list):
    data = get_data(file_list)
    lines_count = len(data[1])
    write_data_list = [data[0]]
    for i in range(lines_count):
        write_data_list.append([row[i] for row in data[1:]])
    with open('info.csv', 'w') as f:
        for row in write_data_list:
            csv.writer(f, quoting=csv.QUOTE_NONNUMERIC).writerow(row)


write_to_csv(test_files)
