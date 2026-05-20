import numpy as np
from scipy.fft import dctn, idctn
import cv2
from PIL import Image
import pywt

# ─────────────────────────────────────────
# Преобразование Арнольда (перемешивание ЦВЗ)
# ─────────────────────────────────────────
def arnold_transform(img, iterations=5):
    N = img.shape[0]
    result = img.copy()
    for _ in range(iterations):
        new = np.zeros_like(result)
        for i in range(N):
            for j in range(N):
                ni = (i + j) % N
                nj = (i + 2 * j) % N
                new[ni, nj] = result[i, j]
        result = new
    return result

def arnold_inverse(img, iterations=5):
    N = img.shape[0]
    result = img.copy()
    for _ in range(iterations):
        new = np.zeros_like(result)
        for i in range(N):
            for j in range(N):
                ni = (2 * i - j) % N
                nj = (-i + j) % N
                new[ni, nj] = result[i, j]
        result = new
    return result

# ─────────────────────────────────────────
# МЕТРИКИ КАЧЕСТВА
# ─────────────────────────────────────────
def psnr(original, watermarked):
    mse = np.mean((original.astype(float) - watermarked.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)

def ncc(wm_original, wm_extracted):
    a = wm_original.astype(float).flatten()
    b = wm_extracted.astype(float).flatten()
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

# ─────────────────────────────────────────
# ВСТРАИВАНИЕ
# ─────────────────────────────────────────
def embed_watermark(container_path, watermark_path, output_path,
                    k=20, arnold_iter=5):
    """
    container_path  – путь к изображению-контейнеру (полутоновое или RGB)
    watermark_path  – путь к бинарному ЦВЗ (любой размер, будет приведён)
    output_path     – путь для сохранения результата
    k               – коэффициент масштабирования (по умолчанию 20)
    arnold_iter     – число итераций преобразования Арнольда
    """
    # Загрузка контейнера (полутоновое)
    container = np.array(Image.open(container_path).convert('L'), dtype=float)
    M = container.shape[0]
    assert container.shape[0] == container.shape[1], "Контейнер должен быть квадратным"

    # Загрузка ЦВЗ — приводим к квадрату, нормализуем до [0,1]
    wm_img = np.array(Image.open(watermark_path).convert('L').resize(
        (M // 4, M // 4), Image.NEAREST), dtype=float)
    N = wm_img.shape[0]
    wm_binary = (wm_img > 127).astype(float)

    # Шаг 1: DCT контейнера
    dct_container = dctn(container, norm='ortho')

    # Шаг 2: DWT Хаара (1 уровень) к коэффициентам DCT
    LL, (LH, HL, HH) = pywt.dwt2(dct_container, 'haar')
    subbands = [LL, LH, HL, HH]

    # Шаг 3: Предобработка ЦВЗ — Арнольд + DCT
    wm_arnold = arnold_transform(wm_binary, arnold_iter)
    dct_wm = dctn(wm_arnold, norm='ortho')

    # Шаг 4: Делим DCT ЦВЗ на 4 равных блока
    h, w = dct_wm.shape
    h2, w2 = h // 2, w // 2
    wm_blocks = [
        dct_wm[:h2, :w2],
        dct_wm[:h2, w2:],
        dct_wm[h2:, :w2],
        dct_wm[h2:, w2:]
    ]

    # Шаг 5: Встраиваем каждый блок ЦВЗ в левый верхний угол каждого поддиапазона
    new_subbands = []
    for i, (sb, wb) in enumerate(zip(subbands, wm_blocks)):
        sb_modified = sb.copy()
        bh, bw = wb.shape
        sb_modified[:bh, :bw] += wb * k
        new_subbands.append(sb_modified)

    # Шаг 6: Обратное DWT
    idwt_result = pywt.idwt2(
        (new_subbands[0], (new_subbands[1], new_subbands[2], new_subbands[3])),
        'haar'
    )

    # Шаг 7: Обратное DCT
    watermarked = idctn(idwt_result, norm='ortho')
    watermarked = np.clip(np.round(watermarked), 0, 255).astype(np.uint8)

    # Сохранение
    Image.fromarray(watermarked).save(output_path)

    # Метрика незаметности
    p = psnr(container, watermarked)
    print(f"[ВСТРАИВАНИЕ] PSNR = {p:.2f} dB")
    print(f"[ВСТРАИВАНИЕ] Результат сохранён: {output_path}")
    return watermarked, wm_binary

# ─────────────────────────────────────────
# ИЗВЛЕЧЕНИЕ
# ─────────────────────────────────────────
def extract_watermark(watermarked_path, original_path, output_wm_path,
                      wm_size, k=20, arnold_iter=5):
    """
    watermarked_path – путь к изображению со встроенным ЦВЗ
    original_path    – путь к исходному изображению-контейнеру
    output_wm_path   – путь для сохранения извлечённого ЦВЗ
    wm_size          – размер ЦВЗ (N×N), использованный при встраивании
    k                – тот же коэффициент масштабирования
    arnold_iter      – то же число итераций Арнольда
    """
    # Загрузка обоих изображений
    img_w = np.array(Image.open(watermarked_path).convert('L'), dtype=float)
    img_o = np.array(Image.open(original_path).convert('L'), dtype=float)

    # DCT обоих
    dct_w = dctn(img_w, norm='ortho')
    dct_o = dctn(img_o, norm='ortho')

    # DWT обоих
    LL_w, (LH_w, HL_w, HH_w) = pywt.dwt2(dct_w, 'haar')
    LL_o, (LH_o, HL_o, HH_o) = pywt.dwt2(dct_o, 'haar')

    subbands_w = [LL_w, LH_w, HL_w, HH_w]
    subbands_o = [LL_o, LH_o, HL_o, HH_o]

    # Размеры блока ЦВЗ
    h2, w2 = wm_size // 2, wm_size // 2

    # Извлечение блоков DCT ЦВЗ из четырёх поддиапазонов
    wm_dct = np.zeros((wm_size, wm_size))
    positions = [
        (slice(None, h2), slice(None, w2)),
        (slice(None, h2), slice(w2, None)),
        (slice(h2, None), slice(None, w2)),
        (slice(h2, None), slice(w2, None)),
    ]
    for i, (sb_w, sb_o, pos) in enumerate(zip(subbands_w, subbands_o, positions)):
        wm_dct[pos] = (sb_w[:h2, :w2] - sb_o[:h2, :w2]) / k  # используем правильный срез

    # Обратное DCT ЦВЗ
    wm_recovered = idctn(wm_dct, norm='ortho')

    # Обратное преобразование Арнольда
    wm_recovered = arnold_inverse(wm_recovered, arnold_iter)

    # Бинаризация
    wm_binary = (wm_recovered > 0.5).astype(np.uint8) * 255

    Image.fromarray(wm_binary).save(output_wm_path)
    print(f"[ИЗВЛЕЧЕНИЕ] ЦВЗ сохранён: {output_wm_path}")
    return wm_binary

# ─────────────────────────────────────────
# ВЫЧИСЛИТЕЛЬНЫЕ ЭКСПЕРИМЕНТЫ
# ─────────────────────────────────────────
def run_experiments(container_path, watermark_path, k_values=[10, 20, 40],
                    jpeg_qualities=[90, 70, 50, 30]):
    import io
    print("=" * 60)
    print("ЭКСПЕРИМЕНТЫ: незаметность и робастность")
    print("=" * 60)

    original = np.array(Image.open(container_path).convert('L'), dtype=float)
    M = original.shape[0]
    wm_img = np.array(Image.open(watermark_path).convert('L').resize(
        (M // 4, M // 4), Image.NEAREST), dtype=float)
    wm_original = (wm_img > 127).astype(float)
    N = wm_img.shape[0]

    for k in k_values:
        print(f"\n--- k = {k} ---")
        # Встраивание
        watermarked, wm_bin = embed_watermark(
            container_path, watermark_path, 'wm_temp.png', k=k)
        p = psnr(original, watermarked)
        print(f"  PSNR (без атаки):   {p:.2f} dB")

        # Без атаки
        wm_ext = extract_watermark(
            'wm_temp.png', container_path, 'wm_ext.png',
            wm_size=N, k=k)
        n = ncc(wm_original * 255, wm_ext)
        print(f"  NCC  (без атаки):   {n:.4f}")

        # JPEG-атаки
        print("  JPEG-сжатие:")
        for q in jpeg_qualities:
            # Применяем JPEG к изображению со встроенным ЦВЗ
            buf = io.BytesIO()
            Image.fromarray(watermarked).save(buf, format='JPEG', quality=q)
            buf.seek(0)
            attacked_img = Image.open(buf)
            attacked_img.save('wm_attacked.jpg')

            wm_ext_attacked = extract_watermark(
                'wm_attacked.jpg', container_path, 'wm_ext_att.png',
                wm_size=N, k=k)
            n_att = ncc(wm_original * 255, wm_ext_attacked)
            print(f"    quality={q:3d}: NCC = {n_att:.4f}")

# ─────────────────────────────────────────
# ГЛАВНОЕ МЕНЮ
# ─────────────────────────────────────────
def main():
    import sys

    print("Выберите режим работы:")
    print("  1 – Встраивание ЦВЗ")
    print("  2 – Извлечение ЦВЗ")
    print("  3 – Вычислительные эксперименты")
    choice = input("Ваш выбор: ").strip()

    if choice == '1':
        container = input("Путь к изображению-контейнеру: ").strip()
        watermark = input("Путь к ЦВЗ (бинарное изображение): ").strip()
        output    = input("Путь для сохранения результата: ").strip()
        k         = int(input("Коэффициент масштабирования k (по умолчанию 20): ").strip() or 20)
        iters     = int(input("Итерации Арнольда (по умолчанию 5): ").strip() or 5)
        embed_watermark(container, watermark, output, k=k, arnold_iter=iters)

    elif choice == '2':
        watermarked = input("Путь к изображению со встроенным ЦВЗ: ").strip()
        original    = input("Путь к исходному изображению-контейнеру: ").strip()
        output_wm   = input("Путь для сохранения извлечённого ЦВЗ: ").strip()
        wm_size     = int(input("Размер ЦВЗ N (N×N, использованный при встраивании): ").strip())
        k           = int(input("Коэффициент масштабирования k (по умолчанию 20): ").strip() or 20)
        iters       = int(input("Итерации Арнольда (по умолчанию 5): ").strip() or 5)
        extract_watermark(watermarked, original, output_wm,
                          wm_size=wm_size, k=k, arnold_iter=iters)

    elif choice == '3':
        container = input("Путь к изображению-контейнеру: ").strip()
        watermark = input("Путь к ЦВЗ: ").strip()
        run_experiments(container, watermark)

    else:
        print("Неверный выбор.")

if __name__ == '__main__':
    main()