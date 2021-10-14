import api.config_api as cp

g = 9

key_list = cp.get_key_list(filep="ru_RU")
key_values = []
for i in key_list:
    if f"code_{g}" in i[1]:
        key_values.append(i[1])
        print(i[1])

for i in key_values:
    print(cp.get_value(i, filep="ru_RU"))