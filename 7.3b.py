# Задание 7.3b
# Сделать копию скрипта задания 7.3a.

# Переделать скрипт:

# Запросить у пользователя ввод номера VLAN.

# Выводить информацию только по указанному VLAN.

# Пример работы скрипта:

# Enter VLAN number: 10
# 10       0a1b.1c80.7000      Gi0/4
# 10       01ab.c5d0.70d0      Gi0/8
# Ограничение: Все задания надо выполнять используя только пройденные темы.

input_vlan = int(input("Enter VLAN number: "))

file = open('CAM_table.txt', 'r')

table = []

for line in file:
    words = line.split()
    if words and words[0].isdigit():
        vlan, mac, typeint, ports = words
        table.append([int(vlan), mac, ports])

print()

for vlan, mac, ports in sorted(table):
    if input_vlan == vlan:
        print(f"{vlan:<9}{mac:20}{ports}")