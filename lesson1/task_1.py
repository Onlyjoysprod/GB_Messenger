# 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и
# проверить тип и содержание соответствующих переменных. Затем с помощью
# онлайн-конвертера преобразовать строковые представление в формат Unicode и также
# проверить тип и содержимое переменных

first_word = 'разработка'
second_word = 'сокет'
third_word = 'декоратор'

print(f'{first_word} тип: {type(first_word)} \n{second_word} тип: {type(second_word)}'
      f'\n{third_word} тип: {type(third_word)}\n')

first_word_trans = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
second_word_trans = '\u0441\u043e\u043a\u0435\u0442'
third_word_trans = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

print(f'{first_word_trans} тип: {type(first_word_trans)} \n{second_word_trans} тип: {type(second_word_trans)}'
      f'\n{third_word_trans} тип: {type(third_word_trans)}')
