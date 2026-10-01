IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]

FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
]

E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1,
]

P = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25,
]

PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4,
]

PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]

SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

SBOXES = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ],
]

def permute(block: int, table: list, in_bits: int) -> int:
    out = 0
    for pos in table:
        out = (out << 1) | ((block >> (in_bits - pos)) & 1)
    return out


def _rotl28(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (28 - shift))) & 0x0FFFFFFF


def generate_subkeys(key8: bytes) -> list:
    if len(key8) != 8:
        raise ValueError("Key DES harus tepat 8 byte.")

    key64 = int.from_bytes(key8, "big")
    key56 = permute(key64, PC1, 64)          
    c = (key56 >> 28) & 0x0FFFFFFF           
    d = key56 & 0x0FFFFFFF                   

    subkeys = []
    for shift in SHIFTS:
        c = _rotl28(c, shift)
        d = _rotl28(d, shift)
        cd = (c << 28) | d                    
        subkeys.append(permute(cd, PC2, 56)) 
    return subkeys


def _feistel(r: int, subkey: int) -> int:
    """Fungsi f(R, K): ekspansi -> XOR subkey -> S-box -> permutasi P."""
    x = permute(r, E, 32) ^ subkey       

    out = 0
    for i in range(8):
        six = (x >> (42 - 6 * i)) & 0x3F     
        row = ((six & 0x20) >> 4) | (six & 1)  
        col = (six >> 1) & 0x0F         
        out = (out << 4) | SBOXES[i][row][col]

    return permute(out, P, 32)             


def des_encrypt_block(block8: bytes, subkeys: list) -> bytes:
    """Enkripsi satu blok 8 byte menggunakan subkey yang diberikan."""
    if len(block8) != 8:
        raise ValueError("Blok DES harus tepat 8 byte.")

    block = permute(int.from_bytes(block8, "big"), IP, 64)
    left = (block >> 32) & 0xFFFFFFFF
    right = block & 0xFFFFFFFF

    for i in range(16):
        left, right = right, left ^ _feistel(right, subkeys[i])

    preoutput = (right << 32) | left
    return permute(preoutput, FP, 64).to_bytes(8, "big")


def des_decrypt_block(block8: bytes, subkeys: list) -> bytes:
    """Dekripsi satu blok 8 byte (subkey dipakai terbalik)."""
    return des_encrypt_block(block8, subkeys[::-1])


def pad_pkcs7(data: bytes) -> bytes:
    """Padding PKCS#7 sampai panjang kelipatan 8."""
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len]) * pad_len


def unpad_pkcs7(data: bytes) -> bytes:
    if not data or len(data) % 8 != 0:
        raise ValueError("Panjang data tidak valid untuk PKCS#7.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 8:
        raise ValueError("Nilai padding tidak valid.")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Padding tidak konsisten (kemungkinan key/ciphertext salah).")
    return data[:-pad_len]


def encrypt_message(plaintext: bytes, key8: bytes) -> bytes:
    subkeys = generate_subkeys(key8)
    data = pad_pkcs7(plaintext)
    out = bytearray()
    for i in range(0, len(data), 8):
        out += des_encrypt_block(data[i:i + 8], subkeys)
    return bytes(out)


def decrypt_message(ciphertext: bytes, key8: bytes) -> bytes:
    if not ciphertext or len(ciphertext) % 8 != 0:
        raise ValueError("Panjang ciphertext harus kelipatan 8 dan tidak kosong.")
    subkeys = generate_subkeys(key8)
    out = bytearray()
    for i in range(0, len(ciphertext), 8):
        out += des_decrypt_block(ciphertext[i:i + 8], subkeys)
    return unpad_pkcs7(bytes(out))
