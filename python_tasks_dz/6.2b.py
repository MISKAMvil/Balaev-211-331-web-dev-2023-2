# Задание 6.2b
# Сделать копию скрипта задания 6.2a.

# Дополнить скрипт: Если адрес был введен неправильно, запросить адрес снова.

# Ограничение: Все задания надо выполнять используя только пройденные темы.

flag = False

while flag == False:
    ip = input('Enter ip: ')
    octets = ip.split('.')
    if len(octets) == 4:
        for octet in octets:
            if not (octet.isdigit() and int(octet) >= 0 and int(octet) <= 255):
                flag = False
                print('IP-адрес записан неверно')
                break
            else: 
                flag = True
        if flag == True:
            print('IP-адрес записан верно')
    else: 
        flag = False
        print('IP-адрес записан неверно')

if flag:
    f_ip = int(octets[0])
    if f_ip <= 223 and f_ip > 0:
        print('unicast')
    elif f_ip <= 239 and f_ip >= 224:
        print('multicast')
    elif ip == '255.255.255.255':
        print('local broadcast')
    elif ip == '0.0.0.0':
        print('unassigned')
    else:
        print('unused')