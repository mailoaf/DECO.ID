import os
import urllib.parse
import html
import base64
import base58
from flask import Flask, jsonify, request, render_template, send_from_directory

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Morse code dictionary
MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', ' ': '/'
}
REVERSE_MORSE_DICT = {v: k for k, v in MORSE_DICT.items() if k != ' '}

# Human-readable names for UI status list
DECODER_NAMES = {
    'unicode': 'Unicode Escape',
    'html': 'HTML Entities',
    'url': 'URL Encode',
    'morse': 'Morse Code',
    'binary': 'Binary',
    'decimal': 'Decimal',
    'octal': 'Octal',
    'base16': 'Base16 (Hex)',
    'base32': 'Base32',
    'base58': 'Base58',
    'base64': 'Base64',
    'base85': 'Base85',
    'ascii85': 'ASCII85',
}

# ----------------- Decoder Functions -----------------

def dbase64(teks):
    try:
        padded = teks.strip()
        if len(padded) % 4 != 0:
            padded += '=' * (4 - len(padded) % 4)
        decode = base64.b64decode(padded.encode('utf-8')).decode('utf-8')
        if not decode.isprintable() or decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dbase16(teks):
    try:
        teks_clean = teks.strip().replace(" ", "").upper()
        decode = base64.b16decode(teks_clean.encode('utf-8')).decode('utf-8')
        if not decode.isprintable() or decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dbase32(teks):
    try:
        teks_clean = teks.strip().replace(" ", "").upper()
        if len(teks_clean) % 8 != 0:
            teks_clean += '=' * (8 - len(teks_clean) % 8)
        decode = base64.b32decode(teks_clean.encode('utf-8')).decode('utf-8')
        if not decode.isprintable() or decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dbase58(teks):
    try:
        teks_clean = teks.strip().replace(" ", "")
        decode = base58.b58decode(teks_clean.encode('utf-8')).decode('utf-8')
        if not decode.isprintable() or decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dbase85(teks):
    try:
        teks_clean = teks.strip().replace(" ", "")
        decode = base64.b85decode(teks_clean.encode('utf-8')).decode('utf-8')
        if not decode.isprintable() or decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def ascii85(teks):
    try:
        teks_clean = teks.strip().replace(" ", "")
        decode = base64.a85decode(teks_clean.encode('utf-8')).decode('utf-8')
        if not decode.isprintable() or decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def durl(teks):
    try:
        if '%' not in teks:
            raise ValueError
        decode = urllib.parse.unquote(teks)
        if decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dhtml(teks):
    try:
        if '&' not in teks or ';' not in teks:
            raise ValueError
        decode = html.unescape(teks)
        if decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dunicode(teks):
    try:
        if '\\u' not in teks and '\\U' not in teks:
            raise ValueError
        decode = teks.encode('utf-8').decode('unicode-escape')
        if decode == teks:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dbinary(teks):
    try:
        teks_clean = teks.strip()
        if ' ' in teks_clean:
            blocks = teks_clean.split()
        else:
            if len(teks_clean) % 8 != 0:
                raise ValueError
            blocks = [teks_clean[i:i+8] for i in range(0, len(teks_clean), 8)]
        for b in blocks:
            if not set(b).issubset({'0', '1'}):
                raise ValueError
        decode = "".join(chr(int(b, 2)) for b in blocks)
        if not decode.isprintable() or decode == "":
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def doctal(teks):
    try:
        teks_clean = teks.strip()
        blocks = teks_clean.split()
        for o in blocks:
            if not set(o).issubset(set('01234567')):
                raise ValueError
        decode = "".join(chr(int(o, 8)) for o in blocks)
        if not decode.isprintable() or decode == "":
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def ddecimal(teks):
    try:
        teks_clean = teks.strip()
        blocks = teks_clean.split()
        for d in blocks:
            if not d.isdigit():
                raise ValueError
        decode = "".join(chr(int(d, 10)) for d in blocks)
        if not decode.isprintable() or decode == "":
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

def dmorse(teks):
    try:
        teks_clean = teks.strip()
        if not set(teks_clean).issubset({'.', '-', ' ', '/', '|'}):
            raise ValueError
        if '.' not in teks_clean and '-' not in teks_clean:
            raise ValueError
        processed = teks_clean.replace('   ', ' / ').replace('  ', ' / ')
        words = processed.replace('|', '/').split('/')
        
        decoded_words = []
        for word in words:
            letters = word.strip().split()
            decoded_letters = []
            for letter in letters:
                if letter in REVERSE_MORSE_DICT:
                    decoded_letters.append(REVERSE_MORSE_DICT[letter])
                else:
                    raise ValueError
            if decoded_letters:
                decoded_words.append("".join(decoded_letters))
        decode = " ".join(decoded_words)
        if not decode:
            raise ValueError
        return True, decode
    except Exception:
        return False, "Format mismatch"

# Decoders order list
DECODERS = {
    'unicode': dunicode,
    'html': dhtml,
    'url': durl,
    'morse': dmorse,
    'binary': dbinary,
    'decimal': ddecimal,
    'octal': doctal,
    'base16': dbase16,
    'base32': dbase32,
    'base58': dbase58,
    'base64': dbase64,
    'base85': dbase85,
    'ascii85': ascii85,
}

# ----------------- Flask Routes -----------------

def score_readability(text):
    if not text:
        return -999.0
    
    text_lower = text.lower()
    total = len(text)
    
    letters = sum(1 for c in text if c.isalpha())
    digits = sum(1 for c in text if c.isdigit())
    spaces = sum(1 for c in text if c.isspace())
    
    common_punc = sum(1 for c in text if c in ",.!? -_:")
    rare_symbols = sum(1 for c in text if c in "{}[]()<>|\\/^+=~`@#$%&*")
    
    good_chars = letters + digits + spaces + common_punc
    ratio = good_chars / total if total > 0 else 0
    penalty = (rare_symbols / total) * 0.5 if total > 0 else 0
    
    score = ratio - penalty
    
    # Bonus for letters and spacing structure
    if letters > 0:
        score += 0.1
    if spaces > 0:
        score += 0.05
        
    # Bonus for common words (case-insensitive)
    import re
    words = re.findall(r'[a-z]+', text_lower)
    common_words = {"kode", "berhasil", "sukses", "flag", "hello", "world", "test", "code", "user", "admin"}
    for w in words:
        if w in common_words:
            score += 0.5
            break
            
    return score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/decode-all', methods=['POST'])
def api_decode_all():
    data = request.json or {}
    text = data.get('text', '')
    if not text:
        return jsonify({'success': False, 'message': 'Empty text', 'results': []})

    results = []
    for key, decoder_func in DECODERS.items():
        success, result = decoder_func(text)
        if success:
            results.append({
                'key': key,
                'name': DECODER_NAMES.get(key, key.upper()),
                'status': 'SUKSES',
                'result': result,
                'score': score_readability(result)
            })
        else:
            results.append({
                'key': key,
                'name': DECODER_NAMES.get(key, key.upper()),
                'status': 'MISMATCH',
                'result': 'Format mismatch',
                'score': -999.0
            })

    # Sort results: Success first, then by readability score descending, mismatch last
    results.sort(key=lambda x: (x['status'] == 'MISMATCH', -x['score']))

    # Only allow the best successful match to remain SUKSES
    best_found = False
    for r in results:
        if r['status'] == 'SUKSES':
            if not best_found:
                best_found = True
            else:
                r['status'] = 'MISMATCH'
                r['result'] = 'Format mismatch'

    return jsonify({
        'success': True,
        'results': results
    })

# Serve static files manually if running locally
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('../static', path)

if __name__ == '__main__':
    app.run(debug=True)
