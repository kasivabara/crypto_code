import collections
import math
import os

# Константы для английского языка
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# Частота появления букв в английском (от самых частых к редким)
ENGLISH_TOP = ("etaoinshrdlcumwfgypbvkjxqz").upper()

def get_factors(n):
    factors = []
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            factors.append(i)
            factors.append(n // i)
    factors.append(n)
    return set(factors)

def find_key_lengths(ciphertext, max_len=20):
    sequences = collections.defaultdict(list)
    for seq_len in range(3, 6):
        for i in range(len(ciphertext) - seq_len):
            seq = ciphertext[i:i + seq_len]
            sequences[seq].append(i)
    
    factor_counts = collections.Counter()
    for positions in sequences.values():
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                diff = positions[i+1] - positions[i]
                for f in get_factors(diff):
                    if f <= max_len:
                        factor_counts[f] += 1
    return [f[0] for f in factor_counts.most_common(5)]

def get_top_candidates(chunk, top_n=3):
    """Оценивает каждый возможный сдвиг и возвращает топ-N вариантов буквы ключа."""
    m = len(ALPHABET)
    scores = []
    for shift in range(m):
        # Дешифруем кусок этим сдвигом
        decoded = "".join([ALPHABET[(ALPHABET.index(c) - shift) % m] for c in chunk])
        counts = collections.Counter(decoded)
        # Считаем "вес": сколько популярных букв англ. языка попало в топ этого куска
        chunk_top = [item[0] for item in counts.most_common(6)]
        score = len(set(chunk_top) & set(ENGLISH_TOP[:6]))
        scores.append((ALPHABET[shift], score))
    
    # Сортируем по убыванию веса
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]

def decrypt_vigenere(ciphertext, key):
    res = []
    m = len(ALPHABET)
    for i, char in enumerate(ciphertext):
        shift = ALPHABET.index(key[i % len(key)])
        res.append(ALPHABET[(ALPHABET.index(char) - shift) % m])
    return "".join(res)

def start_interactive_session(raw_text):
    # Очистка: только буквы A-Z
    ciphertext = "".join([c.upper() for c in raw_text if c.upper() in ALPHABET])
    
    if not ciphertext:
        print("Ошибка: В тексте нет английских букв!")
        return

    # 1. Поиск длины
    lengths = find_key_lengths(ciphertext)
    print(f"\n[*] Анализ Казиски предполагает длины ключа: {lengths}")
    try:
        chosen_len = int(input("[?] Выберите длину ключа для подбора: "))
    except ValueError:
        chosen_len = lengths[0]

    # 2. Подготовка кандидатов для каждой позиции
    all_candidates = []
    for i in range(chosen_len):
        column = ciphertext[i::chosen_len]
        all_candidates.append(get_top_candidates(column))

    # Начальный ключ из самых вероятных вариантов
    current_key = [cand[0][0] for cand in all_candidates]

    # 3. Интерактивный цикл
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        key_str = "".join(current_key)
        decrypted_snippet = decrypt_vigenere(ciphertext[:100], key_str)
        
        print(f"=== Vigenere Interactive Breaker (EN) ===")
        print(f"ТЕКУЩИЙ КЛЮЧ: {key_str}")
        print(f"ПРОСМОТР: {decrypted_snippet}...\n")
        
        print("ВЕРОЯТНЫЕ ВАРИАНТЫ ПО ПОЗИЦИЯМ:")
        for i, cands in enumerate(all_candidates):
            options = " | ".join([f"{char}(score:{s})" for char, s in cands])
            print(f" [{i}] сейчас '{current_key[i]}': {options}")
        
        print("\nУПРАВЛЕНИЕ:")
        print(" - Чтобы сменить букву, введите: <индекс> <буква> (например: 0 K)")
        print(" - Введите 'EXIT' для завершения")
        
        cmd = input("\n> ").strip().upper()
        
        if cmd == 'EXIT':
            print(f"\nИтоговый ключ: {key_str}")
            print(f"Результат: {decrypt_vigenere(ciphertext, key_str)}")
            break
        
        try:
            parts = cmd.split()
            idx = int(parts[0])
            new_char = parts[1]
            if 0 <= idx < chosen_len and new_char in ALPHABET:
                current_key[idx] = new_char
        except:
            input("Ошибка ввода! Используйте формат '0 A'. Нажмите Enter...")

if __name__ == "__main__":
    user_input = input("0. Встроенный пример\n1. Свой пример\n")

    if not (user_input in ["1"]):
        text = "DHWAZYYNKIKEYPDMJFDHWOZRWAFQXTBITMMEFEJMREKLLPCECAQAOAMILCNACAJMNUVTGNRHSCZBCEILADZUXDWZOHORMTZOPOFMOHSSEMVNCTZIOLEXMZTICEKXZCSADTTCRAJIXTORAAOIMOXBCEWOFIMCRYSVYTRALBCEBEKPJUVDTMIOVAOAVGKIFAOLEXMZTIXTZMHOXAJKCYCIFKZTREMVZQEADLDSDRAJPTSOFWAWOADBCROSMTOSPRGUOHOVWZTSDRMKOUBEGNOHOMGVVRMHQTPXERQQNIXENQOALLWBCEBEANOHORAKCSZEFLGIDTDMOHOPGWMWSLDPVVOTGAOABVWBJDOALPDTSSWDZNXEUMNSKRQBCADTZMNPONVQIGYFLPZRSCZACOELVJZPBOHWMTSOFIGTYTZMDNOQMIGIDYGNREKLLPVNNTZIOACWWPVVOADZZANYKIDDVUPCMYCHGCGDSNUZZACESBOHOSSUZRKTWXMOZOJBDOXSAVYIFIVCVLGESTOHRAKQICBESAZDYNDGWEMAMAZSYMWKDTSZWVNHKVWJZEXDWXMIFEVWATREFMXECSABDECOXTDFOTZMMEPOJMDTSSFMXECSSZTTRALBCECEUQOIJEFAMEQAAVRHKTLPZYRANMGOCTKWDNYRVMMTYMSQITKIFIHOXAJKCIMADAOADEDCSUBYECNTSNUZZACEXZJMDHWNVRWEJBJTRESZOICAFBJTREEMMCRAFBOODHWVJBSLABTTYTZMJFPIUQVLCTGBCEXOTTZSDOLPZMKIFBVXMODTZCDOJAJFCTSBZROVWVPECTGBCECONMMESGFWOHOROQNEOVWZTTRIFORIVLHMMICHVCMIXGLPZROIYVJFKUYCNTESLPZRYMSVNEXALMXOWPGAZDYFAUKOBTSVODSGFQOABIWAGAGYWZNAXDHMJPVEVMQODEVBJTREALZACOXBCEZAKBRACAKSZDDOUWMROCLUJRKLKIIDVIEQOLEXMZTAWOFOROWEFQOICIFBZROSLQIGDOJMVDPRGUYIYNSJJUDHGEVRDFMTGYDHWMHPORGZMETEUBZDDHWQIAZPJWKRSALMYEWAFLNOPTZMNEXALWMSKFLMMAVLZMAOENVMYTREEWIABCZGVNNDWAORYYWLOHORWXPBVIULPRSNYBCEBEAOIOPTAJZRSUKBCEKEVQGECSMJHIDTWLOODHWAZNKTWIKRYPGAVLDOJMNTYRWBCEKNUQZNDLSENAQAAVNTVUPCMYDHWMHPORGZRHYWSAIODWABCOETAVNIQHLWKPYSWLOHSSAVOHOPJMNEXTKBVTOOXBCIXGKPZSKIVQOHKSJCDNODLPZROWGCGDLESAOADEZWRWYUDLMOWEWFDSDHGEROELVXMOFIFKZSOXAAOWOWWZZMYDWZVTOWZMIWOWWZZCSTAHZNCOXWILIOFMXIDYTCONYWOMXOXSMUZTREOMVLDHGNOHOWZWGEGOJTYAXDXWMCOMSAOEBSSVYSVANMNTYWGZFFYRMACEMLWIMLISSEOHKTLPZROWSAIOVOFOZRKNQVZENFGZGAGSSOVIXSLTPXERQECEXUFLZRDHWAVMOEEXZRYRLPZSONSBJRGAKINKODLWAOBBALOHOGGDZRXOJAOODACMOHOIJEDVOSOQOHDHWUOODHWXMOFIFKZSNUWBJDEELWOHOTWUKTKTAWISDHWGKRYDMKZDDHWZZTRIKXMOZOKIGWKSSTNOBEBMXTODABRACOTRZCDEVBCADTZMNEFEJQOYYFLPZAXCAMITCHSAIOGGADZNGAQBJAWOJMKLOAKIITGAQWALSFWXZOZLWNZLDTZMTWORWVZENEVVJWYTZMMMYRWANOVUPCMYSSFMXECSSZTFYREWIABCZQXAVSLIOECILQNAVSGVZCOSKIMYPOJLZSZOLQXSDALMNIXTZMAOBMWZNTKTWADTSSSAKEMISTFIXDGNPSOOXBCEPRWMYOWGJIITODLWKEYPDMNEMOFLGYSTAAVSZEUQVLUIFLJFKBMAZOPTZMWEXEXQOSDHSBKEYPDMXAXDWZDVOFJWHTREAZNLKVWZTACLSDZSOTTGCICMSAOEBAKIOYBAFBJVORZQNODHWZNEXSDIQENAFLPNCUJMJFRIKNPTERWPZKXOOAIOYTZMMPVESAPROTZIITREKIOICFSKOIYNGNCICVSVDTIVGTPPDUGCNNOSKIIDRIKUJMONLIMYGHAUNAVLLPDSVESLNTYTZMXOXCDCNIYNLPVTBEHCWLSCKXZRSSZNMOWLMFPRIAFLHOXAJKCIOSXZJMZONMMTI" 
    else:
        text = input("Шифртекст: ")

    start_interactive_session(text)