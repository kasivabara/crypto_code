# PVD steganography for RGB images
# Requirements: pip install opencv-python numpy


import matplotlib.pyplot as plt
from prettytable import PrettyTable
import cv2
import numpy as np
import math

RANGES = [(0,7),(8,15),(16,31),(32,63),(64,127),(128,255)]

def bits_for_range(d):
    for l,u in RANGES:
        if l <= d <= u:
            return int(math.floor(math.log2(u - l + 1))), l
    return 1, 0

def text_to_bits(text):
    b = ''.join(f'{ord(c):08b}' for c in text)
    length = f'{len(b):032b}'
    return length + b

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)

def embed_pair(p1, p2, bits):
    d = abs(int(p1) - int(p2))
    nbits, l = bits_for_range(d)
    if len(bits) < nbits:
        bits += '0' * (nbits - len(bits))
    b = int(bits[:nbits], 2)
    d_new = l + b

    if p1 >= p2:
        p1_new = p2 + d_new
        p2_new = p2
    else:
        p2_new = p1 + d_new
        p1_new = p1

    p1_new = np.clip(p1_new, 0, 255)
    p2_new = np.clip(p2_new, 0, 255)

    return int(p1_new), int(p2_new), bits[nbits:]


def extract_pair(p1, p2):
    d = abs(int(p1) - int(p2))
    nbits, l = bits_for_range(d)
    b = d - l
    return f'{b:0{nbits}b}'

def embed_image(img, message_bits):
    # h, w, c = img.shape
    flat = img.flatten()
    i = 0
    while i < len(flat)-1 and len(message_bits) > 0:
        p1, p2 = flat[i], flat[i+1]
        p1n, p2n, message_bits = embed_pair(p1, p2, message_bits)
        flat[i], flat[i+1] = p1n, p2n
        i += 2
    return flat.reshape(img.shape)

def extract_image(img):
    flat = img.flatten()
    bits = ''
    for i in range(0, len(flat)-1, 2):
        bits += extract_pair(flat[i], flat[i+1])
    msg_len = int(bits[:32], 2)
    return bits[32:32+msg_len]


def mse_psnr(img1, img2):
    mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
    if mse == 0:
        return 0, 100
    psnr = 10 * math.log10((255 ** 2) / mse)
    return mse, psnr

def calculate_ssim(img1, img2):
    # Упрощенная реализация SSIM согласно формуле из задания 
    mu1 = np.mean(img1)
    mu2 = np.mean(img2)
    sigma1_sq = np.var(img1)
    sigma2_sq = np.var(img2)
    sigma12 = np.cov(img1.flatten(), img2.flatten())[0, 1]
    
    K1, K2 = 0.01, 0.03
    L = 255
    C1 = (K1 * L)**2
    C2 = (K2 * L)**2
    
    ssim_val = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2))
    return ssim_val

def ber(original_bits, extracted_bits):
    errors = sum(o != e for o, e in zip(original_bits, extracted_bits))
    return errors / len(original_bits)

def get_max_capacity(img):
    # Расчет максимально возможного объема информации 
    flat = img.flatten()
    total_bits = 0
    for i in range(0, len(flat)-1, 2):
        d = abs(int(flat[i]) - int(flat[i+1]))
        nbits, _ = bits_for_range(d)
        total_bits += nbits
    return total_bits, total_bits / img.size # возвращает (биты, bpp)


def add_noise(img):
    noise = np.random.normal(0, 10, img.shape)
    noisy = img + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def change_brightness(img, value=30):
    return np.clip(img + value, 0, 255).astype(np.uint8)

def jpeg_compress(img, path='temp.jpg'):
    cv2.imwrite(path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    return cv2.imread(path)


def histogram(img, title, save_path=None):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.title(title)
    plt.hist(img.flatten(), bins=256)
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        print(f"  Histogram saved: {save_path}")
    else:
        plt.show()
    plt.close()

def run_experiments(img):
    import os
    os.makedirs("experiments", exist_ok=True)

    max_bits, bpp = get_max_capacity(img)
    print(f"Max capacity: {max_bits} bits ({bpp:.2f} bpp)")

    portions = [0.1, 0.5, 1.0]
    table = PrettyTable(["Load", "Bits", "PSNR (dB)", "SSIM", "Saved files"])

    for p in portions:
        pct = int(p * 100)
        bits_to_embed = int(max_bits * p)

        # формируем фиктивное сообщение нужной длины
        fake_bits = '0' * bits_to_embed

        stego = embed_image(img.copy(), fake_bits)

        mse, psnr = mse_psnr(img, stego)
        ssim_val = calculate_ssim(img, stego)

        # Сохраняем стего-изображение
        stego_path = f"experiments/stego_{pct}pct.png"
        cv2.imwrite(stego_path, stego)
        print(f"  Stego image saved: {stego_path}")

        # Сохраняем гистограммы
        hist_orig_path = f"experiments/hist_original_{pct}pct.png"
        hist_stego_path = f"experiments/hist_stego_{pct}pct.png"
        histogram(img,   f"Original Histogram {pct}%", save_path=hist_orig_path)
        histogram(stego, f"Stego Histogram {pct}%",    save_path=hist_stego_path)

        table.add_row([
            f"{pct}%",
            bits_to_embed,
            f"{psnr:.2f}",
            f"{ssim_val:.4f}",
            f"stego_{pct}pct.png, hist_*_{pct}pct.png"
        ])

    print(table)
    print("All experiment files saved in: experiments/")

def main():
    mode = input("Mode (1-embed / 2-extract): ")

    if mode == '1':
        path = input("Path to RGB image: ")
        img = cv2.imread(path)
        
        if img is None:
            print(f"Ошибка: Изображение по адресу '{path}' не найдено.")
            return
        
        exp = input("Run experiment mode? (y/n): ")
        if exp.lower() == 'y':
            run_experiments(img)
            return

        # 1. Считаем макс. емкость до встраивания 
        max_b, bpp = get_max_capacity(img)
        print(f"Max capacity: {max_b} bits ({bpp:.2f} bpp)")
        
        msg = input(f"Message to embed (max {max_b//8} chars): ")
        bits = text_to_bits(msg)
        
        if len(bits) > max_b:
            print("Error: Message too long!")
            return

        stego = embed_image(img.copy(), bits)
        cv2.imwrite("stego.png", stego)

        # 2. Считаем метрики [cite: 174, 178]
        mse, psnr = mse_psnr(img, stego)
        ssim_val = calculate_ssim(img, stego)
        
        print(f"--- Results ---")
        print(f"MSE: {mse:.4f}")
        print(f"PSNR: {psnr:.2f} dB")
        print(f"SSIM: {ssim_val:.4f}")
        print(f"Actual EC: {len(bits)/img.size:.4f} bpp")

    elif mode == '2':
        path = input("Path to stego image: ")
        img = cv2.imread(path)
        if img is None:
            print(f"Ошибка: Не удалось открыть файл '{path}'. Проверьте путь.")
            return
        bits = extract_image(img)
        text = bits_to_text(bits)
        print("Extracted message:")
        print(text)

        print("\nRobustness test:")
        noisy = add_noise(img)
        bright = change_brightness(img)
        jpeg = jpeg_compress(img)

        for test_img, name in [(noisy,"Noise"),(bright,"Brightness"),(jpeg,"JPEG")]:
            bits2 = extract_image(test_img)
            b = ber(bits, bits2)
            print(f"{name} BER: {b}")

if __name__ == "__main__":
    main()