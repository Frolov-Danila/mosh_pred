import numpy as np

data = np.load("Data.npz")

train_x = data["train_x"]
train_y = data["train_y"]

decode_massive = []

for i in train_y:
    res = ""
    flag = False
    for j in str(i):
        if j.isupper():
            flag = True
        if flag:
            res += j
    decode_massive.append(res)

decode_train_y = np.array(decode_massive)

for x, y in zip(train_x, decode_train_y):
    print(x, y)
    print()
