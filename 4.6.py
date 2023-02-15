# Задание 4.6

# Обработать строку ospf_route и вывести информацию на стандартный поток вывода в виде:

# Prefix                10.0.24.0/24
# AD/Metric             110/41
# Next-Hop              10.0.13.3
# Last update           3d18h
# Outbound Interface    FastEthernet0/0

# Ограничение: Все задания надо выполнять используя только пройденные темы.

ospf_route = "       10.0.24.0/24 [110/41] via 10.0.13.3, 3d18h, FastEthernet0/0"

ospf_route = ospf_route.replace(' via', '').replace(',', '')
ospf_route_to_list = ospf_route.split()
data1, data2, data3, data4, data5 = ospf_route_to_list
data_name1, data_name2, data_name3, data_name4, data_name5 = [
    "Prefix", "AD/Metric", "Next-Hop", "Last update", "Outbound Interface"]

print("{:22} {:22}".format(data_name1, data1))
print("{:22} {:22}".format(data_name2, data2))
print("{:22} {:22}".format(data_name3, data3))
print("{:22} {:22}".format(data_name4, data4))
print("{:22} {:22}".format(data_name5, data5))
