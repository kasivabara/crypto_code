



def clean_text(text: str) -> str:
    """
    Removes all non-alphabetic characters and converts text to uppercase.
    """
    return ''.join(char for char in text if char.isalpha()).upper()

def vigenere_subtract(cipher_char: str, crib_char: str) -> str:
    """
    Subtracts the crib character from the ciphertext character modulo 26.
    Formula: (C - P) mod 26 = K  OR  (C - K) mod 26 = P
    """
    c_val = ord(cipher_char) - ord('A')
    crib_val = ord(crib_char) - ord('A')
    
    # Calculate the original value (Key or Plaintext)
    result_val = (c_val - crib_val) % 26
    return chr(result_val + ord('A'))

def vigenere_add(cipher_char: str, crib_char: str) -> str:
    """
    Subtracts the crib character from the ciphertext character modulo 26.
    Formula: (C - P) mod 26 = K  OR  (C - K) mod 26 = P
    """
    c_val = ord(cipher_char) - ord('A')
    crib_val = ord(crib_char) - ord('A')
    
    # Calculate the original value (Key or Plaintext)
    result_val = (c_val + crib_val) % 26
    return chr(result_val + ord('A'))

def build_right(cyphertext : str, block_key : str, start_position : int):
    return_text = ""

    key = block_key
    i = start_position
    block_iterator = 0
    while (len(cyphertext) - i) > 0:
        plaintext_letter = vigenere_subtract(cyphertext[i], key[block_iterator])
        return_text += plaintext_letter
        key += plaintext_letter
        i += 1
        block_iterator += 1

    return return_text

def build_left(cyphertext : str, block_key : str, start_position : int):

    len_of_text = start_position
    return_text = ["A" for _ in range(len_of_text)]
    key = ["A" for _ in range(len_of_text)]
    
    for i in range(len_of_text):
        
        if (len(block_key) > i):
            return_text[i] = block_key[-(i+1)]
            key[i] = vigenere_subtract(cyphertext[start_position-(i+1)], return_text[i])

        else:
            break
    
    for i2 in range(len_of_text - len(block_key)):
            i = i2 + len(block_key)
            return_text[i] = key[i2]
            key[i] = vigenere_subtract(cyphertext[start_position-(i+1)], return_text[i])


    return ("".join(return_text[::-1]), "".join(key[::-1][:len(block_key)]))

def build_whole(cyphertext : str, block_key : str, start_position : int):
    left, key = build_left(cyphertext, block_key, start_position)
    right = build_right(cyphertext, block_key, start_position)
    return (left + right, key)

def crib_drag_autokey(ciphertext: str, crib: str):
    """
    Performs the crib dragging technique on the ciphertext using the given crib.
    Prints out all possible resulting strings for each position.
    """
    ciphertext = clean_text(ciphertext)
    crib = clean_text(crib)
    
    crib_len = len(crib)
    cipher_len = len(ciphertext)
    
    if crib_len > cipher_len:
        print("Error: Crib cannot be longer than the ciphertext.")
        return

    print(f"--- Crib Dragging Results for '{crib}' ---")
    print(f"{'Pos':<5} | {'Cipher Chunk':<15} | {"Key":<5} | {'Recovered Text (Key/Plaintext)'}")
    print("-" * 60)


    for i in range(cipher_len - crib_len + 1):
        cipher_chunk = ciphertext[i : i + crib_len]
        
        recovered_chunk = ""

        for c_char, crib_char in zip(cipher_chunk, crib):
            recovered_chunk += vigenere_subtract(c_char, crib_char)
        
        plaintext, key = build_whole(ciphertext, recovered_chunk, i)

        print(f"{i:<5} | {cipher_chunk:<15} | {key:<5} | {plaintext}")

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":

    user_input = input("0. Встроенный пример\n1. Свой пример\n")

    if user_input in ["1"]:
        sample_ciphertext = input("Input for ciphertext: ").upper()
        suspected_crib = input("Input for crib: ").upper()
    else:
        sample_ciphertext = "GRPBBGTRMUCHTTGFATIMAMOCKPY"
        suspected_crib = "TEXT"
    
    crib_drag_autokey(sample_ciphertext, suspected_crib)