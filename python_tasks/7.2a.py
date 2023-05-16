# -*- coding: utf-8 -*-
"""
Задание 7.2a

Сделать копию скрипта задания 7.2.

Дополнить скрипт: Скрипт не должен выводить на стандартрый поток вывода команды,
в которых содержатся слова из списка ignore.

При этом скрипт также не должен выводить строки, которые начинаются на !.

Проверить работу скрипта на конфигурационном файле config_sw1.txt.
Имя файла передается как аргумент скрипту.

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

from sys import argv

ignore = ["duplex", "alias", "configuration"]
file = argv[1]

with open(file) as f:
    for line in f:
        if line[0] == '!':
            continue
        has_ignore_word = False
        for ignore_word in ignore:
            if ignore_word in line:
                has_ignore_word = True
                break
        if not has_ignore_word:
            print(line.rstrip())