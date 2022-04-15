# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из
# строкового представления в байтовое и выполнить обратное преобразование (используя
# методы encode и decode).

words = ['разработка', 'администрирование', 'protocol', 'standard']


def encode_decode(word_list):
    result_list = []

    for word in word_list:
        if type(word) == str:
            result_list.append(word.encode('utf-8'))
        elif type(word) == bytes:
            result_list.append(word.decode('utf-8'))
    return result_list


byte_words = encode_decode(words)
print(byte_words)

str_words = encode_decode(byte_words)
print(str_words)
