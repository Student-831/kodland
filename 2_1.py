import random
chars ="+-/*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
pass_length = int(input("Parolanin uzunlugunu belirtiniz: "))
password = ""
for x in range(pass_length):
    password += random.choice(chars)

print("Oluşturulan parola: ", password)
