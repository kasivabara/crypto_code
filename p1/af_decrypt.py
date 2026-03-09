
import string
from math import gcd
from collections import Counter

ALPHABET = string.ascii_lowercase
M = len(ALPHABET)
A, B = 17, 9
letters = ['e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r', 'd', 'l', 'c', 'u', 'm', 'w', 'f', 'g', 'y', 'p', 'b', 'v', 'k', 'x', 'j', 'q', 'z']
words = ["summer", "beautiful", "email", "even", "seven", "blackbird"]


def normalize_text(text):
    return ''.join([c for c in text.lower() if c in ALPHABET]) #просто генератор, который переводит буквы в мелкие

def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

# c -> шифртекст  p -> алфавит
def find_affine_key(p : int, c : int, m=26):
    sollutions = []
    for a in range(m):
        if __import__("math").gcd(a, m) == 1:
            for b in range(m):
                if ((a * p) + b) % m == c:
                    sollutions.append((a, b))
    return sollutions

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

def main():
    text = "Blackbird is not only a bird, but also a powerful software tool written in Python, which is widely used by information security specialists and data researchers to conduct deep open source searches on the global web. This script allows you to automate the process of identifying a specific user's digital footprint on hundreds of different platforms, including social networks, forums, and professional communities, providing a detailed report on the profiles and activities found. Due to its modular architecture and open source code, the project is constantly being developed by the community, adding new features for metadata analysis and visualization of connections between accounts, which makes it an indispensable assistant in the tasks of OSINT and cyber intelligence."
    cipher_text = affine_encrypt(text, A, B)

    print(f"Открытый текст: {text[:30]}...")
    print(f"Шифртекст текст: {cipher_text[:30]}...")
    print("\n\n")

    c = Counter(cipher_text)
    for i in range(len(c.most_common())):
        possible_keys = find_affine_key(ALPHABET.index(letters[i]), ALPHABET.index((c.most_common()[i][0])))

        for key in possible_keys:
            possible_decrypted_plain_text = affine_decrypt(cipher_text, key[0], key[1])

            for word in words:
                if possible_decrypted_plain_text.find(word) != -1:
                    print("Возможный ключ")
                    print(f"a = {key[0]}, b = {key[1]}")
                    print(possible_decrypted_plain_text[:30] + "...")
                    
    return 0



if __name__ == "__main__":
    main()