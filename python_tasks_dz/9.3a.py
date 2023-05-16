# Задание 9.3a
# Сделать копию функции get_int_vlan_map из задания 9.3.

# Дополнить функцию: добавить поддержку конфигурации, когда настройка access-порта выглядит так:
# interface FastEthernet0/20
#  switchport mode access
#  duplex auto
# То есть, порт находится в VLAN 1

# В таком случае, в словарь портов должна добавляться информация, что порт в VLAN 1
# {"FastEthernet0/12": 10,
#  "FastEthernet0/14": 11,
#  "FastEthernet0/20": 1}

# У функции должен быть один параметр config_filename, который ожидает как аргумент имя конфигурационного файла.
# Проверить работу функции на примере файла config_sw2.txt

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

            if 'duplex auto' in line:
                accessl = 1
                if access.get(f'{interface}') == None and trunk.get(f'{interface}') == None:
                    access[interface] = accessl 
    print()
    print('access')
    print(access)
    print('trunk')
    print(trunk)
    print()

get_int_vlan_map('config_sw2.txt')