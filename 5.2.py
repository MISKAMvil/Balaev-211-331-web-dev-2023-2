# Задание 5.2
# Запросить у пользователя ввод IP-сети в формате: 10.1.1.0/24

# Затем вывести информацию о сети и маске в таком формате:

# Network:
# 10        1         1         0
# 00001010  00000001  00000001  00000000

# Mask:
# /24
# 255       255       255       0
# 11111111  11111111  11111111  00000000
# Проверить работу скрипта на разных комбинациях сеть/маска.

# Подсказка: Получить маску в двоичном формате можно так:

# In [1]: "1" * 28 + "0" * 4
# Out[1]: "11111111111111111111111111110000"
# Ограничение: Все задания надо выполнять используя только пройденные темы.

print('\n')
ip_mask = input('Введите IP-сеть в формате: 10.1.1.0/24: ')
# ip_mask = '10.1.1.0/24'
ip = ip_mask[:-3]
mask = ip_mask[-2::]

ip_to_list = ip.split('.')
ip1, ip2, ip3, ip4 = ip_to_list

ip_bin1 = bin(int(ip1))[2:]
ip_bin2 = bin(int(ip2))[2:]
ip_bin3 = bin(int(ip3))[2:]
ip_bin4 = bin(int(ip4))[2:]

mask_bin = '1' * int(mask) + '0' * (32 - int(mask))

print('\n')
print('Network:')
print("{:10}{:10}{:10}{:10}".format(ip1, ip2, ip3, ip4))
print("{:08b}  {:08b}  {:08b}  {:08b}".format(
    int(ip1), int(ip2), int(ip3), int(ip4)))

print('\n')
print('Mask:')
print('/' + mask)
mask1, mask2, mask3, mask4 = mask_bin[0:
                                      8], mask_bin[8:16], mask_bin[16:24], mask_bin[24:32]
print("{:<10}{:<10}{:<10}{:<10}".format(int(mask1, 2),
      int(mask2, 2), int(mask3, 2), int(mask4, 2)))
print("{:10}{:10}{:10}{:10}".format(mask1, mask2, mask3, mask4))

print('\n')
