
from hill_cipher import get_key_matrix, get_key_matrix_inv, matrix_to_key, decrypt
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






test_objects = []
common_words = [
    "available", "copyright", "education", "community", "following",
    "resources", "including", "directory", "insurance", "different",
    "september", "questions", "financial", "equipment", "important",
    "something", "committee", "reference", "companies", "computers",
    "president", "australia", "agreement", "marketing", "solutions",
    "technical", "statement", "downloads", "subscribe", "treatment",
    "knowledge", "currently", "published", "corporate", "customers",
    "materials", "countries", "standards", "political", "advertise",
    "institute", "sponsored", "condition", "effective", "selection",
    "executive", "necessary", "according", "christmas", "furniture",
    "structure", "potential", "documents", "operating", "developed",
    "telephone", "therefore", "christian", "worldwide", "publisher",
    "excellent", "interface", "operation", "beautiful", "locations",
    "providing", "authority", "programme", "employees", "relations",
    "completed", "otherwise", "character", "functions", "submitted",
    "regarding", "increased", "beginning", "specified", "sometimes",
    "transport", "galleries", "presented", "secretary", "magazines",
    "francisco", "described", "attention", "situation", "emergency",
    "determine", "difficult", "satellite", "recommend", "professor",
    "generally", "continued", "component", "guarantee", "processes"
]



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

        # key_matrix = get_key_matrix(item.key, item.block)
        # key_matrix_inv = get_key_matrix_inv()
        # ciphertext_matrix = np.transpose(np.linalg.matmul(key_matrix, known_plaintext_matrix) % 26)
        # ciphertext = ""
        # for row in range(item.block):
        #     for column in range(item.block):
        #         possible_plaintext += chr(ciphertext_matrix[row][column] + ord('A') )
  

        print(f"Key: {item.key}\nReal text: {item.plaintext[:len(item.key)]}\nCiphertext: {item.cyphertext[:len(item.key)]}\nPossible plaintext: {possible_plaintext[:len(item.key)]}\n")
        print(f"Does the texts match? -> {item.plaintext[:len(item.key)] == possible_plaintext[:len(item.key)]}\n\n\n")
    
    if item.type_of_cipher == "2":
        ciphertext_matrix = np.transpose(get_key_matrix(item.cyphertext[:len(item.key)], item.block))
        
        known_plaintext = item.plaintext[:len(item.key)]
        known_plaintext_matrix = np.transpose(get_key_matrix(known_plaintext, item.block))
        known_plaintext_matrix_inv = get_key_matrix_inv(matrix_to_key(known_plaintext_matrix), item.block)


        possible_key_matrix = np.linalg.matmul(ciphertext_matrix, known_plaintext_matrix_inv) % M

        # ---
        ciphertext_matrix_2 = np.transpose(get_key_matrix(item.cyphertext[:len(item.key2)], item.block))

    
