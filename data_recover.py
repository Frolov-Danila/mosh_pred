import numpy as np

data = np.load("Data.npz")

train_x = data["train_x"]
train_y = data["train_y"]

decode_massive = []
decode_set = []
decode_dict = {}

for i in train_y:
    res = ""
    flag = False
    for j in str(i):
        if j.isupper():
            flag = True
        if flag:
            res += j
    decode_massive.append(res)
    if not(res in decode_set):
        decode_set.append(res)
    
for i in range(len(decode_set)):
    decode_dict[decode_set[i]] = i

print(decode_dict)