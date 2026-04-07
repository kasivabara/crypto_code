



import numpy as np
from math import gcd, sqrt, isqrt
import string 

ALPHABET = string.ascii_uppercase + " _-"
M = len(ALPHABET)


def char_to_int(c):
    return ALPHABET.index(c)

def int_to_char(i):
    return ALPHABET[i % M]

def is_perfect_sq(num):
    if num < 0:
        return False  # Negative numbers cannot be perfect squares
    
    r = isqrt(num)
    return r * r == num

def matrix_to_key(matrix):
    key = ""

    rows, cols = matrix.shape

    for i in range(rows):
        for j in range(cols):
            key += int_to_char(int(matrix[i][j]) % M)

    return key

def get_validated_message(block : int):
    message = str(input("Enter the message: ")).upper()
    # добавляет символы, чтобы разбить по блочно
    if len(message) % block != 0:
        message = message.ljust( len(message) + (block - (len(message) % block)) % block, "_")
    return message

def get_key_matrix(key, block):
    key_matrix = np.zeros((block, block), dtype=int)
    k = 0
    for i in range(block):
        for j in range(block):
            key_matrix[i][j] = char_to_int(key[k])
            k += 1
    return key_matrix

def get_validated_key(mode="1"):
    key = "XX"
    
    if mode == "1":
        while True:
            key = str(input("Enter the key: ")).upper()

            if not is_perfect_sq(len(key)):
                print("\nKey must have lenght for n*n matrix\n")
                continue

            block = int(sqrt(len(key)))
            det_mod = int(round(np.linalg.det(get_key_matrix(key, block)))) % M

            if gcd(det_mod, M) != 1:
                print(f"\nKey matrix is not invertible modulo {M}\n")
                continue

            break
        return key

    if mode == "2":
        return_keys = []

        while True:
            key1 = str(input("Enter the first key: ")).upper()

            if not is_perfect_sq(len(key1)):
                print("\nKey must have lenght for n*n matrix\n")
                continue

            block = int(sqrt(len(key1)))
            det_mod = int(round(np.linalg.det(get_key_matrix(key1, block)))) % M

            if gcd(det_mod, M) != 1:
                print(f"\nKey matrix is not invertible modulo {M}\n")
                continue
            
            return_keys.append(key1)
            break

        while True:
            key2 = str(input("Enter the second key: ")).upper()

            if len(return_keys[0]) != len(key2):
                print("Error: keys must have the same size.")
                continue

            if not is_perfect_sq(len(key2)):
                print("\nKey must have lenght for n*n matrix\n")
                continue

            block = int(sqrt(len(key2)))
            det_mod = int(round(np.linalg.det(get_key_matrix(key2, block)))) % M
            if gcd(det_mod, M) != 1:
                print(f"\nKey matrix is not invertible modulo {M}\n")
                continue

            return_keys.append(key2)
            break

        return return_keys
    
    raise KeyError(f"Mode value is not supported: {mode}")



def get_choice() -> str:

    """
    '1/2 + e/d'

    1 -> Hill cypher\n
    2 -> Hill recurent cypher\n
    e -> Encryption\n
    d -> Decryption
    """

    cypher_method = "XXX"
    enc_or_dec = "XXX"

    while not (cypher_method in ["1", "2"]):
        cypher_method = input("Hill cypher (1)\nHill recurent cypher (2)\nChoose the cypher method: ")
    
    print("\n")

    while not (enc_or_dec[0] in ["e", "d"]):
        enc_or_dec = str(input("Encryption (e)\nDecryption (d)\nChoose the action: ")).lower()[0]
    
    print("\n")

    return cypher_method + enc_or_dec




def get_key_matrix_inv(key, block):

    f'''
    действуя по формулам
    A * A^(-1) == 1 [mod {M}]
    A^(-1) = [1/det(A)] * adj(A)
    A^(-1) == [ det^(-1)(A) mod {M} ] * adj(A) [mod {M}]
    adj(A) = det(A) * A^(-1)
    '''

    key_matrix = get_key_matrix(key, block)
    det = int(round(np.linalg.det(key_matrix)))
    det_mod = det % M
    det_inv = 0

    # поиск мультипликативной обратной к det по mod
    for i in range(M):
        if (det_mod * i) % M == 1:
            det_inv = i
            break

    if det_inv == 0:
        raise ValueError("Det inverse is zero")

    # adj(A) = det(A) * A^(-1)
    adjugate = np.round(det * np.linalg.inv(key_matrix)).astype(int)

    # A^(-1) == [ det^(-1)(A) mod _ ] * adj(A) [mod _]
    key_matrix_inv = (det_inv * adjugate) % M

    return key_matrix_inv
    


def encrypt(message, key, mode, key2=None):

    # not recurent
    if (mode == "1"):

        block = int(sqrt(len(key)))
        cipher_vector = np.zeros((block, 1), dtype=int)
        message_vector = np.zeros((block, 1), dtype=int)
        key_matrix = get_key_matrix(key, block)
        ciphertext = ""

        index = 0
        while (index < len(message)):
            for row in range(block):
                message_vector[row][0] = char_to_int(message[index + row])

            cipher_vector = np.matmul(key_matrix, message_vector) % M

            for row in range(block):
                ciphertext += int_to_char(int(cipher_vector[row][0]))
            
            index += block

        return ciphertext
    
    # recurent
    if (mode == "2"):

        block = int(sqrt(len(key))) #так как матрицы должны быть n*n, то и блоки при перемножении будут одинаковыми
        cipher_vector = np.zeros((block, 1), dtype=int)
        message_vector = np.zeros((block, 1), dtype=int)
        k1, k2 = get_key_matrix(key, block), get_key_matrix(key2, block)
        k_i = []
        ciphertext = ""

        index = 0
        while (index < len(message)):

            if (index//block) == 0:
                k_i = k1
            elif (index//block) == 1:
                k_i = k2
            else:
                k_i = np.matmul(k1, k2) % M
                k1, k2 = k2, k_i

            for row in range(block):
                message_vector[row][0] = char_to_int(message[index + row])

            cipher_vector = np.matmul(k_i, message_vector) % M

            for row in range(block):
                ciphertext += int_to_char(int(cipher_vector[row][0]))
            
            index += block
        
        return ciphertext
    
    raise KeyError(f"Mode value is not supported: {mode}")


def decrypt(cipher_text, key, mode, key2=None):

    # not recurent
    if (mode == "1"):
        block = int(sqrt(len(key)))
        cipher_vector = np.zeros((block, 1), dtype=int)
        message_vector = np.zeros((block, 1), dtype=int)
        key_matrix_inv = get_key_matrix_inv(key, block)
        plaintext = ""

        for index in range(0, len(cipher_text), block):
            for row in range(block):
                cipher_vector[row][0] = char_to_int(cipher_text[index + row])

            message_vector = np.matmul(key_matrix_inv, cipher_vector) % M

            for row in range(block):
                plaintext += int_to_char(int(message_vector[row][0]))

        return plaintext

    # recurent
    if (mode == "2"):
        
        block = int(sqrt(len(key))) #так как матрицы должны быть n*n, то и блоки при перемножении будут одинаковыми
        cipher_vector = np.zeros((block, 1), dtype=int)
        message_vector = np.zeros((block, 1), dtype=int)
        k1, k2 = get_key_matrix(key, block), get_key_matrix(key2, block)
        k_i = []
        plaintext = ""

        index = 0
        while (index < len(cipher_text)):

            if (index//block) == 0:
                k_i = k1
            elif (index//block) == 1:
                k_i = k2
            else:
                k_i = np.matmul(k1, k2) % M
                k1, k2 = k2, k_i

            k_i_inv = get_key_matrix_inv(matrix_to_key(k_i), block)

            for row in range(block):
                message_vector[row][0] = char_to_int(cipher_text[index + row])

            cipher_vector = np.matmul(k_i_inv, message_vector) % M

            for row in range(block):
                plaintext += int_to_char(int(cipher_vector[row][0]))
            
            index += block
        
        return plaintext

    raise KeyError(f"Mode value is not supported: {mode}")



def main():


    choice = get_choice()

    # not recurent
    if choice[0] == "1":

        # encryption
        if choice[1] == "e":
            key = get_validated_key()
            block = int(sqrt(len(key)))
            message = get_validated_message(block)
            cipher_text = encrypt(message, key, choice[0])

            print(f"\nCipher text: {cipher_text}")
        
        # decryption
        if choice[1] == "d":
            key = get_validated_key()
            block = int(sqrt(len(key)))
            cipher_text = get_validated_message(block)
            plaintext = decrypt(cipher_text, key, choice[0])

            print(f"\nMessage text: {plaintext}")
        
    
    # recurent
    if choice[0] == "2":

        # encryption
        if choice[1] == "e":
            key1, key2 = get_validated_key(choice[0])
            block = int(sqrt(len(key1)))
            message = get_validated_message(block)
            cipher_text = encrypt(message, key1, choice[0], key2)

            print(f"\nCipher text: {cipher_text}")
        
        # decryption
        if choice[1] == "d":      
            key1, key2 = get_validated_key(choice[0])
            block = int(sqrt(len(key1)))
            cipher_text = get_validated_message(block)
            plaintext = decrypt(cipher_text, key1, choice[0], key2)

            print(f"\nMessage text: {plaintext}")


if __name__ == "__main__":
    main()