
from hill_cipher import get_key_matrix, get_key_matrix_inv, matrix_to_key, decrypt
import numpy as np
from math import sqrt

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

class test_item():
    def __init__(self, type_of_cipher, key, plaintext, cyphertext):
        self.type_of_cipher = type_of_cipher
        self.key = key
        self.block = int(sqrt(len(key)))
        self.plaintext = plaintext
        self.cyphertext = cyphertext

with open('test_text.txt', 'r', encoding='utf-8') as file:
    for line in file:
        temp = line.strip().split("|")
        if temp[0] != "1":
            continue
        test_objects.append(test_item(temp[0], temp[1], temp[2], temp[3]))
        # type_of_cipher | key | plaintext | cyphertext


"""

K * P = C
K = C * P^(-1)

"""
for item in test_objects:
    item: test_item
    if not (item.type_of_cipher == "1"):
        continue


    ciphertext_matrix = np.transpose(get_key_matrix(item.cyphertext[:len(item.key)], item.block))
    
    known_plaintext = item.plaintext[:len(item.key)]
    known_plaintext_matrix = np.transpose(get_key_matrix(known_plaintext, item.block))
    known_plaintext_matrix_inv = get_key_matrix_inv(matrix_to_key(known_plaintext_matrix), item.block)
    possible_key_matrix = np.linalg.matmul(ciphertext_matrix, known_plaintext_matrix_inv)
    possible_plaintext = decrypt(item.cyphertext, matrix_to_key(possible_key_matrix), "1")

    # key_matrix = get_key_matrix(item.key, item.block)
    # key_matrix_inv = get_key_matrix_inv()
    # ciphertext_matrix = np.transpose(np.linalg.matmul(key_matrix, known_plaintext_matrix) % 26)
    # ciphertext = ""
    # for row in range(item.block):
    #     for column in range(item.block):
    #         possible_plaintext += chr(ciphertext_matrix[row][column] + ord('A') )
    print(possible_plaintext)

    # print(f"Key: {known_plaintext} | matrix:\n{plaintext_matrix} |\nciphertext: {ciphertext} |\n Real ciphertext: {item.cyphertext[:len(item.key)]}")

    
