# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
# Написать скрипт, автоматизирующий его заполнение данными.
#
# Для этого:
# Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
# цена (price), покупатель (buyer), дата (date).
# Функция должна предусматривать запись данных в виде словаря в файл orders.json.
# При записи данных указать величину отступа в 4 пробельных символа;
# Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.

# {"orders": []}

import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json', encoding='utf-8') as f:
        f_content = f.read()
        obj = json.loads(f_content)
    if obj and 'orders' in obj.keys():
        orders_to_write = obj['orders']
    else:
        orders_to_write = []
    orders_new = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    }
    orders_to_write.append(orders_new)
    dict_to_json = {'orders': orders_to_write}
    with open('orders.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(dict_to_json, indent=4, ensure_ascii=False))


write_order_to_json('001', 3, 1890.9, 'Алекс228', '17.04.2022')
