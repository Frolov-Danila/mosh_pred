import numpy as np
import json

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
            if not(j.isalpha()):
                flag = False
                continue
            res += j
    decode_massive.append(res)
    if not(res in decode_set):
        decode_set.append(res)
    
for i in range(6):
    decode_dict[i] = decode_set[i]
