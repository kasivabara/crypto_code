
from hill_cipher import get_key_matrix, get_key_matrix_inv, matrix_to_key, decrypt, get_padded_text, char_to_int, int_to_char
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

def final_output(item : test_item, possible_plaintext : str, mode="1"):

    c_w = 18 #minimal_column_width

    if mode == "1":

        if c_w < len(item.key):
            c_w += (len(item.key) - c_w) + 2

        print(f"{"Key":<{c_w}} | {"Real text":<{c_w}} | {"Ciphertext":<{c_w}} | {"Pos. plaintext":<{c_w}}")
        print(f"{item.key:<{c_w}} | {item.plaintext[:len(item.key)] + "...":<{c_w}} | {item.cyphertext[:len(item.key)] + "...":<{c_w}} | {possible_plaintext[:len(item.key)] + "...":<{c_w}}")
        print(f"Does the texts match? -> {get_padded_text(item.plaintext, item.block) == possible_plaintext}")

    elif mode == "2":

        if c_w < ((len(item.key)*2) + 3):
            c_w += (((len(item.key)*2) + 3) - c_w) + 2
        
        print(f"{"Key 1":<{c_w}} | {"Key 2":<{c_w}} | {"Real text":<{c_w}} | {"Ciphertext":<{c_w}} | {"Pos. plaintext":<{c_w}} ")
        print(f"{item.key:<{c_w}} | {item.key2:<{c_w}} | {item.plaintext[:len(item.key)*2] + "...":<{c_w}} | {item.cyphertext[:len(item.key)*2] + "...":<{c_w}} | {possible_plaintext[:len(item.key)*2] + "...":<{c_w}}")
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

mode1_items = [obj for obj in test_objects if obj.type_of_cipher == "1"]
mode2_items = [obj for obj in test_objects if obj.type_of_cipher == "2"]


"""

K * P = C
K = C * P^(-1)

"""
print("Просто шифр Хилла")
for item in mode1_items:
    item: test_item

    if item.type_of_cipher == "1":
        ciphertext_matrix = np.transpose(get_key_matrix(item.cyphertext[:len(item.key)], item.block))
        
        known_plaintext = item.plaintext[:len(item.key)]
        known_plaintext_matrix = np.transpose(get_key_matrix(known_plaintext, item.block))
        known_plaintext_matrix_inv = get_key_matrix_inv(matrix_to_key(known_plaintext_matrix), item.block)


        possible_key_matrix = np.linalg.matmul(ciphertext_matrix, known_plaintext_matrix_inv) % M
        possible_plaintext = decrypt(item.cyphertext, matrix_to_key(possible_key_matrix), "1") 

        print("-" * 40)
        final_output(item, possible_plaintext, mode="1")
        print("-" * 40)
        print()


print("Рекуррентный шифр Хилла")
if len(mode2_items) >= 3:
    block = mode2_items[0].block
    
    #K1
    P1_cols = []
    C1_cols = []
    
    for i in range(3):
        p_block = [char_to_int(c) for c in mode2_items[i].plaintext[:block]]
        c_block = [char_to_int(c) for c in mode2_items[i].cyphertext[:block]]
        P1_cols.append(p_block)
        C1_cols.append(c_block)
    
    P1_mat = np.array(P1_cols).T
    C1_mat = np.array(C1_cols).T
    
    try:
        P1_inv = get_key_matrix_inv(matrix_to_key(P1_mat), block)
        possible_K1 = np.linalg.matmul(C1_mat, P1_inv) % M
    except ValueError:
        print("Матрица P1 неинвертируема. Нужно выбрать другие сообщения.")

    #K2
    P2_cols = []
    C2_cols = []
    
    for i in range(3):
        p_block = [char_to_int(c) for c in mode2_items[i].plaintext[block : block*2]]
        c_block = [char_to_int(c) for c in mode2_items[i].cyphertext[block : block*2]]
        P2_cols.append(p_block)
        C2_cols.append(c_block)
        
    P2_mat = np.array(P2_cols).T
    C2_mat = np.array(C2_cols).T
    
    try:
        P2_inv = get_key_matrix_inv(matrix_to_key(P2_mat), block)
        possible_K2 = np.linalg.matmul(C2_mat, P2_inv) % M
    except ValueError:
        print("Матрица P2 неинвертируема.")


    key1_str = matrix_to_key(possible_K1)
    key2_str = matrix_to_key(possible_K2)

    for item in mode2_items:
        possible_plaintext = decrypt(item.cyphertext, key1_str, "2", key2=key2_str)
        print("-" * 40)
        final_output(item, possible_plaintext, mode="2") 
        print("-" * 40)
        print()