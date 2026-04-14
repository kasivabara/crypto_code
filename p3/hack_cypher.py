import string
from collections import Counter
from math import gcd
from functools import reduce
from c import gamma_autokey_plaintext, gamma_repeating_key

ALPHABET = string.ascii_uppercase
M = len(ALPHABET)

# -------------------------
# ВСПОМОГАТЕЛЬНЫЕ
# -------------------------

def clean_text(text):
    return ''.join([c for c in text.upper() if c in ALPHABET])


def char_to_int(c):
    return ALPHABET.index(c)


def int_to_char(i):
    return ALPHABET[i % M]


class test_item():
    def __init__(self, mode, key, plaintext, ciphertext):
        self.mode = mode
        self.key = key
        self.plaintext = plaintext
        self.ciphertext = ciphertext


test_objects = []
with open('test_text.txt', 'r', encoding='utf-8') as file:
    found = False
    for line in file:
        temp = line.strip("\n").split("|")

        if temp[0] == "p3":
            found = True
            continue

        if temp[0] == "p3e":
            break

        if found:
            test_objects.append(test_item(temp[0], temp[1], temp[2], temp[3]))



# -------------------------
# 1. KASISKI EXAMINATION
# -------------------------

def find_repeated_sequences(text, seq_len=3):
    sequences = {}
    for i in range(len(text) - seq_len):
        seq = text[i:i+seq_len]
        for j in range(i + seq_len, len(text) - seq_len):
            if text[j:j+seq_len] == seq:
                if seq not in sequences:
                    sequences[seq] = []
                sequences[seq].append(j - i)
    return sequences


def kasiski(text):
    text = clean_text(text)
    seqs = find_repeated_sequences(text)

    distances = []
    for seq in seqs:
        distances.extend(seqs[seq])

    if not distances:
        return []

    def gcd_list(lst):
        return reduce(gcd, lst)

    g = gcd_list(distances)

    # возможные длины ключа
    candidates = [i for i in range(2, 21) if g % i == 0]

    return candidates


# -------------------------
# 2. INDEX OF COINCIDENCE
# -------------------------

def index_of_coincidence(text):
    N = len(text)
    freqs = Counter(text)
    if N < 2:
        return 0
    ic = sum(f * (f - 1) for f in freqs.values()) / (N * (N - 1))
    return ic


def guess_key_length_ic(text, max_len=20):
    text = clean_text(text)
    scores = {}

    for r in range(1, max_len + 1):
        groups = ['' for _ in range(r)]

        for i, c in enumerate(text):
            groups[i % r] += c

        ic_avg = sum(index_of_coincidence(g) for g in groups) / r
        scores[r] = ic_avg

    # сортируем по близости к 0.065 (английский)
    sorted_lengths = sorted(scores, key=lambda x: abs(scores[x] - 0.065))

    return sorted_lengths[:5]


# -------------------------
# 3. ВОССТАНОВЛЕНИЕ КЛЮЧА
# -------------------------

ENGLISH_FREQ = {
    'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
    'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3,
    'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4, 'W': 2.4,
    'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5,
    'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.1, 'Z': 0.07
}


def chi_squared(text):
    N = len(text)
    freqs = Counter(text)

    chi = 0
    for c in ALPHABET:
        observed = freqs.get(c, 0)
        expected = ENGLISH_FREQ[c] * N / 100
        chi += (observed - expected) ** 2 / expected

    return chi


def break_vigenere(ciphertext, key_len):
    ciphertext = clean_text(ciphertext)

    key = ""

    for i in range(key_len):
        group = ''.join(ciphertext[j] for j in range(i, len(ciphertext), key_len))

        best_shift = 0
        best_score = float('inf')

        for shift in range(M):
            decrypted = ''.join(
                int_to_char((char_to_int(c) - shift) % M) for c in group
            )

            score = chi_squared(decrypted)

            if score < best_score:
                best_score = score
                best_shift = shift

        key += int_to_char(best_shift)

    return key


# -------------------------
# 4. ДЕШИФРОВАНИЕ
# -------------------------

def decrypt(ciphertext, key):
    ciphertext = clean_text(ciphertext)
    key = clean_text(key)

    gamma = (key * (len(ciphertext) // len(key) + 1))[:len(ciphertext)]

    result = ""
    for c, g in zip(ciphertext, gamma):
        x = (char_to_int(c) - char_to_int(g)) % M
        result += int_to_char(x)

    return result


# -------------------------
# MAIN
# -------------------------

def crack(ciphertext):
    print("Kasiski candidates:", kasiski(ciphertext))

    ic_candidates = guess_key_length_ic(ciphertext)
    print("IC candidates:", ic_candidates)

    for key_len in ic_candidates:
        key = break_vigenere(ciphertext, key_len)
        plaintext = decrypt(ciphertext, key)

        print("\n---")
        print("Key length:", key_len)
        print("Key:", key)
        print("Text:", plaintext[:200])


if __name__ == "__main__":
    text = input("Enter ciphertext: ")
    crack(text)