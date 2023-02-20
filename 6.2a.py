# Задание 6.2a
# Сделать копию скрипта задания 6.2.

# Добавить проверку введенного IP-адреса. Адрес считается корректно заданным, если он:
# состоит из 4 чисел (а не букв или других символов)
# числа разделенны точкой
# каждое число в диапазоне от 0 до 255

# Если адрес задан неправильно, выводить сообщение: «Неправильный IP-адрес».
# Сообщение «Неправильный IP-адрес» должно выводиться только один раз,
# даже если несколько пунктов выше не выполнены.

# Ограничение: Все задания надо выполнять используя только пройденные темы.

ip = input('Enter ip: ')
# for symbol in ip:
#    if not (symbol.isdigit() or symbol == '.'):
octets = ip.split('.')
flag = True

if len(octets) == 4:
   for octet in octets:
      if not (octet.isdigit() and int(octet) >= 0 and int(octet) <= 255):
         flag = False
         break
else: 
   flag = False

if not(flag):
   print('Неправильный IP-адрес')
else:
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