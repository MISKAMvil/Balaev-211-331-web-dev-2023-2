# Задание 9.3

# Создать функцию get_int_vlan_map, которая обрабатывает конфигурационный файл коммутатора и возвращает кортеж из двух словарей:

#     словарь портов в режиме access, где ключи номера портов, а значения access VLAN (числа):
# {"FastEthernet0/12": 10,
#  "FastEthernet0/14": 11,
#  "FastEthernet0/16": 17}

#     словарь портов в режиме trunk, где ключи номера портов, а значения список разрешенных VLAN (список чисел):
# {"FastEthernet0/1": [10, 20],
#  "FastEthernet0/2": [11, 30],
#  "FastEthernet0/4": [17]}

# У функции должен быть один параметр config_filename, который ожидает как аргумент имя конфигурационного файла.
# Проверить работу функции на примере файла config_sw1.txt

# Ограничение: Все задания надо выполнять используя только пройденные темы.

def get_int_vlan_map(config_filename):
    access = {}
    trunk = {}
    with open(config_filename) as f:
        for line in f:
            if 'interface' in line:
                interface = line.split()[1]
            if 'switchport trunk allowed' in line:
                trunkl = (line.replace(',', ' ').split()[4:])
                int_trunkl = [int(i) for i in trunkl]
                trunk[interface] = int_trunkl
            elif 'switchport access vlan' in line:
                accessl = int(line.split()[-1])
                access[interface] = accessl
    print()
    print('access')
    print(access)
    print('trunk')
    print(trunk)
    print()

get_int_vlan_map('config_sw2.txt')