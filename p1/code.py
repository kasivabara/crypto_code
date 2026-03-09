import string
from math import gcd

ALPHABET = string.ascii_lowercase
M = len(ALPHABET)


def normalize_text(text):
    return ''.join([c for c in text.lower() if c in ALPHABET]) #просто генератор, который переводит буквы в мелкие


# ==============================
# 1. Шифр простой замены
# ==============================

# проверка по длинне и соотвестсвию всех 26 букв
def validate_substitution_key(key):
    key = key.lower()
    if len(key) != M:
        return False
    if set(key) != set(ALPHABET):
        return False
    return True

#Шифруем
def substitution_encrypt(text, key):
    text = normalize_text(text)
    table = {ALPHABET[i]: key[i] for i in range(M)} #формируем dict в котором делаем ключ-значение оригинала в шифр
    return ''.join(table[c] for c in text) #Используем dict для шифровки текста

#Разшифруем (обратная логика)
def substitution_decrypt(text, key):
    text = normalize_text(text)
    table = {key[i]: ALPHABET[i] for i in range(M)} 
    return ''.join(table[c] for c in text)


# ==============================
# 2. Аффинный шифр
# ==============================

#a^(-1)
def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            print(x)
            return x
    return None

# наибольшиый общий делитель должен быть 1
def validate_affine_key(a):
    return gcd(a, M) == 1


def affine_encrypt(text, a, b):
    text = normalize_text(text)
    return ''.join(
        ALPHABET[(a * ALPHABET.index(c) + b) % M] for c in text
    )


def affine_decrypt(text, a, b):
    text = normalize_text(text)
    a_inv = mod_inverse(a, M)
    return ''.join(
        ALPHABET[(a_inv * (ALPHABET.index(c) - b)) % M] for c in text
    )


# ==============================
# 3. Аффинный рекуррентный шифр
# ==============================

def affine_recurrent_encrypt(text, a1, b1, a2, b2):
    text = normalize_text(text)
    result = []

    a_prev, b_prev = a1, b1
    a_curr, b_curr = a2, b2

    for i, c in enumerate(text): # (i,c) -> (0, "k"), (1, "a"), ...
        if i == 0:
            a, b = a_prev, b_prev #base вариант
        elif i == 1:
            a, b = a_curr, b_curr #base2 вариант
        else:
            # считаем новые значения
            a_new = (a_prev * a_curr) % M
            b_new = (b_prev + b_curr) % M
            #перезаписываем для будущего шифровния
            a_prev, a_curr = a_curr, a_new
            b_prev, b_curr = b_curr, b_new
            #записываем для текущего шифрования
            a, b = a_curr, b_curr

        encrypted = ALPHABET[(a * ALPHABET.index(c) + b) % M] #шифруем
        result.append(encrypted)

    return ''.join(result)


def affine_recurrent_decrypt(text, a1, b1, a2, b2):
    text = normalize_text(text)
    result = []

    a_prev, b_prev = a1, b1
    a_curr, b_curr = a2, b2

    for i, c in enumerate(text):
        if i == 0:
            a, b = a_prev, b_prev
        elif i == 1:
            a, b = a_curr, b_curr
        else:
            a_new = (a_prev * a_curr) % M
            b_new = (b_prev + b_curr) % M
            a_prev, a_curr = a_curr, a_new
            b_prev, b_curr = b_curr, b_new
            a, b = a_curr, b_curr

        a_inv = mod_inverse(a, M)
        decrypted = ALPHABET[(a_inv * (ALPHABET.index(c) - b)) % M]
        result.append(decrypted)

    return ''.join(result)


# ==============================
# Интерфейс
# ==============================

def main():
    while True:
        print("\nВыберите шифр:")
        print("1 - Простая замена")
        print("2 - Аффинный")
        print("3 - Аффинный рекуррентный")
        print("0 - Выход")

        choice = input(">> ")

        if choice == "0":
            break

        text = input("Введите текст: ")

        mode = input("1 - Шифрование, 2 - Расшифрование: ")

        if choice == "1":
            key = input("Введите ключ (26 букв): ")
            if not validate_substitution_key(key):
                print("Некорректный ключ")
                continue

            if mode == "1":
                print(substitution_encrypt(text, key))
            else:
                print(substitution_decrypt(text, key))

        elif choice == "2":
            a = int(input("Введите a: "))
            b = int(input("Введите b: "))

            if not validate_affine_key(a):
                print("Некорректный ключ (a должно быть взаимно просто с 26)")
                continue

            if mode == "1":
                print(affine_encrypt(text, a, b))
            else:
                print(affine_decrypt(text, a, b))

        elif choice == "3":
            a1 = int(input("Введите a1: "))
            b1 = int(input("Введите b1: "))
            a2 = int(input("Введите a2: "))
            b2 = int(input("Введите b2: "))
        

            if mode == "1":
                print(affine_recurrent_encrypt(text, a1, b1, a2, b2))
            else:
                print(affine_recurrent_decrypt(text, a1, b1, a2, b2))


if __name__ == "__main__":
    main()
