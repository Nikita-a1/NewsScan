fruits = ["банан", "яблоко"]

for i in range(len(fruits)):
    fruits.insert(i*2 + 1, fruits[i].capitalize())

print(fruits)