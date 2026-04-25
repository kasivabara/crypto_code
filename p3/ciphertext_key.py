def clean_text(text: str) -> str:
    """Оставляет только буквы и переводит в верхний регистр."""
    return ''.join(char for char in text if char.isalpha()).upper()

def vigenere_subtract(cipher_char: str, key_char: str) -> str:
    """
    Вычитает символ ключа из символа шифртекста.
    Формула: P = (C - K) mod 26
    """
    c_val = ord(cipher_char) - ord('A')
    k_val = ord(key_char) - ord('A')
    
    result_val = (c_val - k_val) % 26
    return chr(result_val + ord('A'))

def direct_mathematical_recovery(ciphertext: str, max_length: int = 15):
    """
    Прямое восстановление самоключа по шифртексту.
    Перебирает возможные длины лозунга (L).
    """
    ciphertext = clean_text(ciphertext)
    
    if not ciphertext:
        print("Ошибка: Пустой текст.")
        return

    print("--- Прямое математическое восстановление (Autokey Ciphertext) ---")
    print("Первые L символов неизвестны (отмечены '*'), так как они зашифрованы лозунгом.")
    print("-" * 70)
    
    for L in range(1, max_length + 1):
        if L >= len(ciphertext):
            break
            
        recovered_text = ["*"] * L  # Первые L символов мы восстановить пока не можем
        
        for i in range(L, len(ciphertext)):
            p_char = vigenere_subtract(ciphertext[i], ciphertext[i - L])
            recovered_text.append(p_char)
            
        preview = "".join(recovered_text)
        print(f"Длина лозунга L={L:<2} | {preview}")


if __name__ == "__main__":
    
    user_input = input("0. Встроенный пример\n1. Свой пример\n")

    if user_input == "1":
        sample_ciphertext = input("Введите шифртекст: ").upper()
        max_len = input("Введите максимальную длинну поиска: ")
        try:
            max_len = int(max_len)
            direct_mathematical_recovery(sample_ciphertext, max_len)
        except:
            direct_mathematical_recovery(sample_ciphertext)
    else:
        sample_ciphertext = "WSYZQJHSSRHRSKZCRTKQCCHVAGM"
        direct_mathematical_recovery(sample_ciphertext, 8)

