# PVD steganography for RGB images
# Requirements: pip install opencv-python numpy

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

def mse_psnr(img1, img2):
    mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
    if mse == 0:
        return 0, 100
    psnr = 10 * math.log10((255 ** 2) / mse)
    return mse, psnr

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
    h, w, c = img.shape
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

def histogram(img, title):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.title(title)
    plt.hist(img.flatten(), bins=256)
    plt.show()

def add_noise(img):
    noise = np.random.normal(0, 10, img.shape)
    noisy = img + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def change_brightness(img, value=30):
    return np.clip(img + value, 0, 255).astype(np.uint8)

def jpeg_compress(img, path='temp.jpg'):
    cv2.imwrite(path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    return cv2.imread(path)

def ber(original_bits, extracted_bits):
    errors = sum(o != e for o, e in zip(original_bits, extracted_bits))
    return errors / len(original_bits)

def main():
    mode = input("Mode (1-embed / 2-extract): ")

    if mode == '1':
        path = input("Path to RGB image: ")
        img = cv2.imread(path)
        msg = input("Message to embed: ")
        bits = text_to_bits(msg)

        stego = embed_image(img.copy(), bits)
        cv2.imwrite("stego.png", stego)

        mse, psnr = mse_psnr(img, stego)
        print(f"MSE: {mse}")
        print(f"PSNR: {psnr}")

        histogram(img, "Original histogram")
        histogram(stego, "Stego histogram")

        print("Saved as stego.png")

    elif mode == '2':
        path = input("Path to stego image: ")
        img = cv2.imread(path)
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