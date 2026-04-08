
from hill_cipher import get_key_matrix, get_key_matrix_inv, matrix_to_key, decrypt, get_padded_text
import numpy as np
from math import sqrt
import string

ALPHABET = string.ascii_uppercase + " _-"
M = len(ALPHABET)



class test_item():
    def __init__(self, type_of_cipher, key, plaintext, cyphertext, key2=None):
        self.type_of_cipher = type_of_cipher
        self.key = key
        self.key2 = key2
        self.block = int(sqrt(len(key)))
        self.plaintext = plaintext
        self.cyphertext = cyphertext

def final_output(item_object : test_item, possible_plaintext : str):
    c_w = 18 #minimal_column_width
    if c_w < len(item.key):
        c_w += (len(item.key) - c_w) + 2

    print(f"{"Key":<{c_w}} | {"Real text":<{c_w}} | {"Ciphertext":<{c_w}} | {"Pos. plaintext":<{c_w}}")
    print(f"{item.key:<{c_w}} | {item.plaintext[:len(item.key)] + "...":<{c_w}} | {item.cyphertext[:len(item.key)] + "...":<{c_w}} | {possible_plaintext[:len(item.key)] + "...":<{c_w}}")
    print(f"Does the texts match? -> {get_padded_text(item.plaintext, item.block) == possible_plaintext}")

test_objects = []




with open('test_text.txt', 'r', encoding='utf-8') as file:
    for line in file:
        temp = line.strip("\n").split("|")
        if (temp[0] == "1"):
            test_objects.append(test_item(temp[0], temp[1], temp[2], temp[3]))
            # type_of_cipher | key | plaintext | cyphertext
        if (temp[0] == "2"):
            test_objects.append(test_item(temp[0], temp[1], temp[3], temp[4], key2=temp[2]))
            # type_of_cipher | key_1 | key_2 | plaintext | cyphertext



"""

K * P = C
K = C * P^(-1)

"""
for item in test_objects:
    item: test_item

    if item.type_of_cipher == "1":
        ciphertext_matrix = np.transpose(get_key_matrix(item.cyphertext[:len(item.key)], item.block))
        
        known_plaintext = item.plaintext[:len(item.key)]
        known_plaintext_matrix = np.transpose(get_key_matrix(known_plaintext, item.block))
        known_plaintext_matrix_inv = get_key_matrix_inv(matrix_to_key(known_plaintext_matrix), item.block)


        possible_key_matrix = np.linalg.matmul(ciphertext_matrix, known_plaintext_matrix_inv) % M
        possible_plaintext = decrypt(item.cyphertext, matrix_to_key(possible_key_matrix), "1") 

        final_output(item, possible_plaintext)
        print("-" * 40)



    
    if item.type_of_cipher == "2":
        ciphertext_matrix = np.transpose(get_key_matrix(item.cyphertext[:len(item.key)], item.block))
        
        known_plaintext = item.plaintext[:len(item.key)]
        known_plaintext_matrix = np.transpose(get_key_matrix(known_plaintext, item.block))
        known_plaintext_matrix_inv = get_key_matrix_inv(matrix_to_key(known_plaintext_matrix), item.block)


        possible_key_matrix = np.linalg.matmul(ciphertext_matrix, known_plaintext_matrix_inv) % M

        # ---
        ciphertext_matrix_2 = np.transpose(get_key_matrix(item.cyphertext[:len(item.key2)], item.block))

    
