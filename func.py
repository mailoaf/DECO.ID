import dataclasses
import urllib.parse
import html
import base64
import base58
usr = input("masukkan encoded text: ")


def dbase64(teks):
    try:
        decode1 = base64.b64decode(teks).decode('utf-8')
        return f"[Base64] Berhasil: {decode1}"
    except Exception:
        return "[Base64] Gagal: Format tidak cocok"

def dbase16(teks):
    try:
        decode2 = base64.b16decode(teks.upper()).decode('utf-8')
        return f"[Base16] Berhasil: {decode2}"
    except Exception:
        return "[Base16] Gagal: Format tidak cocok"

def dbase32(teks):
    try:
        decode3 = base64.b32decode(teks).decode('utf-8')
        return f"[Base32] Berhasil: {decode3}"
    except Exception:
        return "[Base32] Gagal: Format tidak cocok"

def dbase58(teks):
    try:
        decode4 = base58.b58decode(teks).decode('utf-8')
        return f"[Base58] Berhasil: {decode4}"
    except Exception:
        return "[Base58] Gagal: Format tidak cocok"

def dbase85(teks):
    try:
        decode5 = base64.b85decode(teks).decode('utf-8')
        return f"[Base85] Berhasil: {decode5}"
    except Exception:
        return "[Base85] Gagal: Format tidak cocok"

def ascii85(teks):
    try:
        decode6 = base64.a85decode(teks).decode('utf-8')
        return f"[ASCII85] Berhasil: {decode6}"
    except Exception:
        return "[ASCII85] Gagal: Format tidak cocok"

def durl(teks):
    try:
        if '%' not in teks:
            raise ValueError
        decode7 = urllib.parse.unquote(teks)
        return f"[URL] Berhasil: {decode7}"
    except Exception:
        return "[URL] Gagal: Format tidak cocok"

def dhtml(teks):
    try:
        if '&' not in teks or ';' not in teks:
            raise ValueError
        decode8 = html.unescape(teks)
        if decode8 == teks:
            raise ValueError
        return f"[HTML] Berhasil: {decode8}"
    except Exception:
        return "[HTML] Gagal: Format tidak cocok"

def dunicode(teks):
    try:
        if '\\u' not in teks:
            raise ValueError
        decode9 = teks.encode('utf-8').decode('unicode-escape')
        if decode9 == teks:
            raise ValueError
        return f"[Unicode] Berhasil: {decode9}"
    except Exception:
        return "[Unicode] Gagal: Format tidak cocok"

def dbinary(teks):
    try:
        teks_clean1 = teks.strip()
        if ' ' in teks_clean1:
            blocks = teks_clean1.split()
        else:
            if len(teks_clean1) % 8 != 0:
                raise ValueError
            blocks = [teks_clean1[i:i+8] for i in range(0, len(teks_clean1), 8)]
        for b in blocks:
            if not set(b).issubset({'0', '1'}):
                raise ValueError
        decode9 = "".join(chr(int(b, 2)) for b in blocks)
        if not decode9.isprintable() or decode9 == "":
            raise ValueError
        return f"[Binary] Berhasil: {decode9}"
    except Exception:
        return "[Binary] Gagal: Format tidak cocok"

def doctal(teks):
    try:
        teks_clean2 = teks.strip()
        blocks = teks_clean2.split()
        for o in blocks:
            if not set(o).issubset(set('01234567')):
                raise ValueError
        decode10 = "".join(chr(int(o, 8)) for o in blocks)
        if not decode10.isprintable() or decode10 == "":
            raise ValueError
        return f"[Octal] Berhasil: {decode10}"
    except Exception:
        return "[Octal] Gagal: Format tidak cocok"

def ddecimal(teks):
    try:
        teks_clean3 = teks.strip()
        blocks = teks_clean3.split()
        for d in blocks:
            if not d.isdigit():
                raise ValueError
        decode11 = "".join(chr(int(d, 10)) for d in blocks)
        if not decode11.isprintable() or decode11 == "":
            raise ValueError
        return f"[Decimal] Berhasil: {decode11}"
    except Exception:
        return "[Decimal] Gagal: Format tidak cocok"

def dmorse(teks):
    try:
        teks_clean = teks.strip()
        if not set(teks_clean).issubset({'.', '-', ' ', '/', '|'}):
            raise ValueError
        if '.' not in teks_clean and '-' not in teks_clean:
            raise ValueError
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9'
        }
        processed = teks_clean.replace('   ', ' / ').replace('  ', ' / ')
        
        words = processed.replace('|', '/').split('/')
        
        decoded_words = []
        for word in words:
            letters = word.strip().split()
            decoded_letters = []
            for letter in letters:
                if letter in morse_dict:
                    decoded_letters.append(morse_dict[letter])
                else:
                    raise ValueError             
            if decoded_letters:
                decoded_words.append("".join(decoded_letters))
        
        decode12 = " ".join(decoded_words)
        if not decode12:
            raise ValueError
        return f"[Morse] Berhasil: {decode12}"
    except Exception:
        return "[Morse] Gagal: Format tidak cocok"

daftar_hasil = [
    (dunicode(usr)), 
    (dhtml(usr)),    
    (durl(usr)),  
    (dmorse(usr)),   
    (dbinary(usr)),  
    (ddecimal(usr)), 
    (doctal(usr)),   
    (dbase16(usr)),  
    (dbase32(usr)),  
    (dbase58(usr)),  
    (dbase64(usr)),  
    (dbase85(usr)),  
    (ascii85(usr))   
]

plaintext = " "
jenis = " "

for hasil in daftar_hasil:
    if hasil:
        parts = hasil.split(" ", 1)

        if len(parts) ==2:
            teks_jenis = parts[0] 
            teks_pesan = parts[1]
            if teks_pesan.lower().startswith("berhasil"):
                plaintext = teks_pesan.split(" ",1)[1]
                jenis = teks_jenis
                break

if plaintext and plaintext.strip() and not plaintext.startswith("b'"):
    print("--- DECODE SUKSES ---")
    print(f"Jenis Encoding : {jenis}")
    print(f"Hasil Decode   : {plaintext}")
else:
    print("Gagal men-decode teks atau hasil decode tidak valid.")