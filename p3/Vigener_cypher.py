import string

ALPHABET = string.ascii_uppercase
M = len(ALPHABET)

def clean_text(text): return ''.join(c for c in text.upper() if c in ALPHABET)

def char_to_int(c): return ALPHABET.index(c)

def int_to_char(i): return ALPHABET[i % M]



# ГЕНЕРАЦИЯ ГАММЫ

def gamma_repeating_key(key, length):
    if not key:
        raise ValueError("Empty key")
    key = clean_text(key)
    repeating = (length // len(key) + 1) #Сколько раз повторить ключ + 1, чтобы хватило
    return (key * repeating)[:length]


def gamma_autokey_plaintext(key, plaintext):
    if not key:
        raise ValueError("Empty key")
    key = clean_text(key)
    plaintext = clean_text(plaintext)
    gamma = key + plaintext
    return gamma[:len(plaintext)]


# ШИФРОВАНИЕ / ДЕШИФРОВАНИЕ
def encrypt_vigenere(plaintext, key, mode):
    plaintext = clean_text(plaintext)
    key = clean_text(key)

    if not key:
        raise ValueError("Empty key")

    result = ""

    # - повторение короткого лозунга;
    if mode == 1:
        gamma = gamma_repeating_key(key, len(plaintext))
        for x1, x2 in zip(plaintext, gamma):
            result += int_to_char(char_to_int(x1) + char_to_int(x2))

    # - самоключ Виженера по открытому тексту;
    elif mode == 2:
        gamma = gamma_autokey_plaintext(key, plaintext)
        for x1, x2 in zip(plaintext, gamma):
            result += int_to_char(char_to_int(x1) + char_to_int(x2))

    # - самоключ Виженера по шифртексту;
    elif mode == 3:
        gamma_list = list(key)
        for i in range(len(plaintext)):
            g = gamma_list[i]
            cipher_char = int_to_char(char_to_int(plaintext[i]) + char_to_int(g))
            result += cipher_char
            # Добавляем зашифрованный символ в гамму для использования через len(key) шагов
            if len(gamma_list) < len(plaintext):
                gamma_list.append(cipher_char)

    else:
        raise ValueError("Invalid mode")

    return result


def decrypt_vigenere(ciphertext, key, mode):
    ciphertext = clean_text(ciphertext)
    key = clean_text(key)

    if not key:
        raise ValueError("Empty key")

    result = ""

    if mode == 1:
        gamma = gamma_repeating_key(key, len(ciphertext))
        for c, g in zip(ciphertext, gamma):
            result += int_to_char(char_to_int(c) - char_to_int(g))

    elif mode == 2:
        # Самоключ по ОТ: гамма строится из РАСШИФРОВАННЫХ символов
        gamma_list = list(key)
        for i in range(len(ciphertext)):
            g = gamma_list[i]
            plain_char = int_to_char(char_to_int(ciphertext[i]) - char_to_int(g))
            result += plain_char
            # Полученный символ открытого текста идет в конец гаммы
            if len(gamma_list) < len(ciphertext):
                gamma_list.append(plain_char)

    elif mode == 3:
        # Самоключ по ШТ: гамма — это просто Ключ + Шифртекст
        gamma = (key + ciphertext)[:len(ciphertext)]
        for c, g in zip(ciphertext, gamma):
            result += int_to_char(char_to_int(c) - char_to_int(g))

    else:
        raise ValueError("Invalid mode")

    return result


def main():
    try:
        mode = int(input("Mode (1/2/3): "))
        if mode not in (1, 2, 3):
            raise ValueError

        action = input("e/d: ").lower()
        text = input("Text: ")
        key = input("Key: ")

        if action == 'e':
            print(encrypt_vigenere(text, key, mode))
        elif action == 'd':
            print(decrypt_vigenere(text, key, mode))
        else:
            raise ValueError("Invalid action")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()