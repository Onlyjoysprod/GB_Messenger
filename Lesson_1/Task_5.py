# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из
# байтовового в строковый тип на кириллице.

import chardet
import subprocess
import platform


def ping_site(url):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '2', url]
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        result = chardet.detect(line)
        print(f'result: {result}')
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))


ping_site('yandex.ru')
ping_site('youtube.com')






