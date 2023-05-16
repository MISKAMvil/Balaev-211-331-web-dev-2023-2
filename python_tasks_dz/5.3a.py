# Задание 5.3a

# Дополнить скрипт из задания 5.3 таким образом, чтобы, в зависимости от выбранного режима, задавались разные вопросы
# в запросе о номере VLANа или списка VLANов:
#     для access: «Введите номер VLAN:»
#     для trunk: «Введите разрешенные VLANы:»

# Ограничение: Все задания надо выполнять используя только пройденные темы.
# То есть эту задачу можно решить без использования условия if и циклов for/while.

access_template = [
    "switchport mode access", "switchport access vlan {}",
    "switchport nonegotiate", "spanning-tree portfast",
    "spanning-tree bpduguard enable"
]

trunk_template = [
    "switchport trunk encapsulation dot1q", "switchport mode trunk",
    "switchport trunk allowed vlan {}"
]

question = {'access': 'Введите номер VLAN: ',
            'trunk': 'Введите разрешенные VLANы: '}

print('\n')
# input_mode = 'trunk'
input_mode = input('Введите режим работы интерфейса (access/trunk): ')
# type = 'Fa0/7'
type = input('Введите тип и номер интерфейса: ')
# vlan = '1, 2, 10'
vlan = input(f"{question[input_mode]}")
print('\n')

mode = {'access': access_template, 'trunk': trunk_template}

print('interface ' + type)
print('\n'.join(mode[input_mode]).format(vlan))
