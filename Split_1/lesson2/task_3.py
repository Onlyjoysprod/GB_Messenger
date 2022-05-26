# 3. Задание на закрепление знаний по модулю yaml. Написать скрипт,
# автоматизирующий сохранение данных в файле YAML-формата.
#
# Для этого:
# Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
# третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом,
# отсутствующим в кодировке ASCII (например, €);
# Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
# При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
# а также установить возможность работы с юникодом: allow_unicode = True;
# Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.

import yaml


some_dict = {
    'list_key': ['some', 'list', 'контент'],
    'int_key': 27,
    'dict_key': {
        'simbol_1': '1€',
        'simbol_2': '2€',
        'simbol_3': '3€'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(some_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open('file.yaml', encoding='utf-8') as f:
    f_content = yaml.load(f, Loader=yaml.FullLoader)
    print(f_content == some_dict)
