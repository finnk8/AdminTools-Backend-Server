import json

str = "[12, 13]"
str_2 = json.loads(str)
str_2.append(14)
print(type(json.dumps(str_2)))