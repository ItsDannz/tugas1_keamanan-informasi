# Tugas 1 Keamanan Informasi - Komunikasi 2 Arah 

| Nama           | NRP        |
| ---            | ---        |
| Hazza Danta Hermandanu               | 5025241117           |

## Screenshot
### Receiver (VM Ubuntu)
<img width="545" height="134" alt="WhatsApp Image 2026-10-01 at 06 37 21" src="https://github.com/user-attachments/assets/89504333-4045-4292-a8d9-7884b561b9f4" />

### Sender (Windows)
<img width="707" height="220" alt="image" src="https://github.com/user-attachments/assets/842db971-c64e-4f82-ba11-65346ba6ed24" />

### Wireshark
<img width="897" height="85" alt="image" src="https://github.com/user-attachments/assets/5e8b6a1f-6411-42b9-864d-77ba38a77293" />


## Penjelasan Code
### common.py
Semua hal berulang yang digunakan sender & receiver: mengirim/menerima pesan
utuh lewat TCP, konversi hex, dan validasi key.
1. Import library
   ```python
   import struct
   ```
2. Deklarasi Konstanta
   ```python
   MAX_PAYLOAD = 1 << 20 #batas panjang 1 frame

   CTRL_QUIT = b"QUIT" #penanda akhiri sesi
   ```
3. `send_frame(sock, payload)`
   ```python
   def send_frame(sock, payload: bytes) -> None:
     header = struct.pack(">I", len(payload))
     sock.sendall(header + payload)
   ```
   - struct.pack mengubah angka menjadi byte dengan format tertentu. Kode format ">I" berarti:
      - `>` = big-endian (byte paling signifikan di depan)
      - `I` = unsigned integer 32 bit (4 byte)
   - Header dan payload digabung menjadi satu buffer lalu dikirim.
   <br>
4. `_recv_exact(sock, n)`
   ```python
   def _recv_exact(sock, n: int):
     buf = bytearray()
     while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
     return bytes(buf)
   ```
   - `buf = bytearray()`: penampung yang bisa ditambah efisien.
   - `while len(buf) < n`: ulangi selama belum terkumpul n byte.
   - `sock.recv(n - len(buf))`: minta sisanya saja, bukan n lagi. Jadi tidak pernah "kebanyakan" membaca dan menelan awal frame berikutnya.
   - `if not chunk: return None`: recv mengembalikan b"" (kosong) kalau lawan menutup koneksi. Fungsi mengembalikan None sebagai sinyal "koneksi putus".
   - `buf += chunk`: tambahkan potongan yang diterima.
   - `return bytes(buf)`: ubah ke bytes immutable.
   <br>
5. `recv_frame(sock)`
   ```python
   def recv_frame(sock):
     header = _recv_exact(sock, 4)
     if header is None:
        return None

     (length,) = struct.unpack(">I", header)
     if length == 0:
        return b""
     if length > MAX_PAYLOAD:
        raise ValueError(f"Panjang frame tidak wajar: {length} byte.")

     payload = _recv_exact(sock, length)
     return payload
   ```
   - `_recv_exact(sock, 4)` membaca tepat 4 byte. Cek header, jika None maka koneksi sudah ditutup dan akan mereturn `None`.
   - `struct.unpack(">I", header)` mengubah 4 byte header kembali menjadi angka `length`.
   - Jika `length` = 0, maka return frame kosong
   - Jika `length` > `MAX_PAYLOAD`, maka tampilkan error
   - Selan itu baca `length` byte payload dengan `_recv_exact`
   <br>
6. `to_hex(data)` dan `from_hex(text)`
   ```python
   def to_hex(data: bytes) -> str:
     return data.hex().upper()

   def from_hex(text: str) -> bytes:
     return bytes.fromhex(text)
   ```
   - `to_hex`: `bytes.hex()` menghasilkan huruf kecil, lalu diubah ke kapital dengan `.upper()`.
   - `from_hex`: `bytes.fromhex` tidak peduli huruf besar/kecil dan mengabaikan spasi.
   <br>
7. `key_from_config(raw)`
   ```python
   key_from_config(raw)
     if isinstance(raw, bytes):
      data = raw
     elif isinstance(raw, str) and raw.lower().startswith("0x"):
       data = bytes.fromhex(raw[2:])
     else:
       data = raw.encode("utf-8")
     if len(data) != 8:
          raise ValueError(
              f"KEY harus tepat 8 byte (saat ini {len(data)} byte). "
              "Gunakan 8 karakter ASCII atau hex 16 digit dengan awalan 0x."
          )
      return data
   ```
   - `isinstance(raw, bytes)`: jika `KEY` sudah berupa `bytes`, maka pakai langsung.
   - `raw.lower().startswith("0x")`: jika `KEY` berupa hex, ambil bagian setelah `0x` lalu ubah dengan `bytes.fromhex`.
   - `else`: selain itu anggap `KEY` sebagai string ASCII biasa, encode ke UTF-8.
   - Validasi panjang harus 8 byte, jika tidak maka `raise ValueError`.
   <br>
   
   
### des.py
Inti algoritma **DES yang diimplementasikan manual dari nol** (sesuai FIPS 46-3) plus padding
PKCS#7 dan mode ECB. File ini murni algoritma — tidak tahu menahu soal jaringan.

1. Tabel-tabel DES (konstanta)
   ```python
   IP = [58, 50, 42, 34, 26, 18, 10, 2,
         60, 52, 44, 36, 28, 20, 12, 4,
         ... ]                       # 64bit, permutasi awal
   FP = [40, 8, 48, 16, 56, 24, 64, 32,
         ... ]                       # 64bit, permutasi akhir (inverse IP)
   E  = [32, 1, 2, 3, 4, 5,
         4, 5, 6, 7, 8, 9,
         ... ]                       # 48bit, expand 32 -> 48 bit
   P  = [16, 7, 20, 21, 29, 12, 28, 17,
         ... ]                       # 32bit, permutasi hasil S-box
   PC1 = [57, 49, 41, 33, 25, 17, 9,
          ... ]                      # 56bit, pilih 56 bit dari key 64 bit
   PC2 = [14, 17, 11, 24, 1, 5,
          ... ]                      # 48bit, hasilkan subkey 48 bit
   SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
   SBOXES = [
       # S1
       [
           [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
           [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
           [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
           [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
       ],
       # S2 ... S8 (pola sama)
   ]
   ```
   - `IP`/`FP` = 64 bit, `E` = 48 bit, `P` = 32 bit, `PC1` = 56 bit,
     `PC2` = 48 bit.
   - `SHIFTS` = jumlah geser kiri tiap round (total 16 round).
   - `SBOXES[i]` = S-box ke-(i+1), berbentuk **4 baris × 16 kolom**; tiap kotak mengubah
     6 bit input menjadi 4 bit output.
   <br>
3. `permute(block, table, in_bits)`
   ```python
   def permute(block: int, table: list, in_bits: int) -> int:
       out = 0
       for pos in table:
           out = (out << 1) | ((block >> (in_bits - pos)) & 1)
       return out
   ```
   - `out = 0`: out dimulai 0.
   - `for pos in table`: ambil bit masukan satu per satu sesuai urutan tabel (dari kiri).
   - `(block >> (in_bits - pos)) & 1`: geser bit ke posisi paling kanan
     lalu ambil 1 bit. Karena penomoran 1-based dari kiri, bit ke-`pos` ada di pergeseran
     `in_bits - pos`.
   - `out = (out << 1) | ...`: gabung bit hasil ke out dari kiri.
   <br>
4. `_rotl28(value, shift)`
   ```python
   def _rotl28(value: int, shift: int) -> int:
       return ((value << shift) | (value >> (28 - shift))) & 0x0FFFFFFF
   ```
   - Rotasi kiri 28-bit, dipakai untuk menggeser blok C dan D di key schedule.
   - `(value << shift)`: geser kiri.
   - `| (value >> (28 - shift))`: bit melebihi batas ke kiri dipindahkan ke kanan (rotasi).
   - `& 0x0FFFFFFF`: mask untuk memastikan hasil tetap 28 bit.
   <br>
5. `generate_subkeys(key8)`
   ```python
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
   ```
   - Validasi key harus 8 byte.
   - `int.from_bytes(key8, "big")`: ubah 8 byte menjadi integer 64 bit.
   - `permute(key64, PC1, 64)`: buang 8 bit paritas menjadi 56 bit.
   - `c` = 28 bit atas, `d` = 28 bit bawah.
   - Loop 16 kali: geser `c` dan `d`, gabung jadi 56 bit (`cd`), lalu `PC2` yang akan menghasilkan subkey 48 bit.
   - Mereturn 16 subkey, `subkeys[0]` untuk round 1 … `subkeys[15]` untuk round 16.
   <br>
6. `_feistel(r, subkey)`
   ```python
   def _feistel(r: int, subkey: int) -> int:
       x = permute(r, E, 32) ^ subkey         

       out = 0
       for i in range(8):
           six = (x >> (42 - 6 * i)) & 0x3F    
           row = ((six & 0x20) >> 4) | (six & 1) 
           col = (six >> 1) & 0x0F             
           out = (out << 4) | SBOXES[i][row][col]

       return permute(out, P, 32)              
   ```
   - `permute(r, E, 32)`: ekspansi 32 menjadi 48 bit, lalu `^ subkey` (XOR dengan subkey round).
   - Loop 8 kali untuk 8 S-box; `(x >> (42 - 6 * i)) & 0x3F` mengambil grup ke-i dari kiri.
   - `row`: dibentuk dari bit ke-1 dan ke-6 (`six & 0x20` digeser, plus `six & 1`).
   - `col`: dibentuk dari bit ke 2-5 (`(six >> 1) & 0x0F`).
   - `SBOXES[i][row][col]`: nilai substitusi 4 bit, digabung ke `out`.
   - `permute(out, P, 32)`: permutasi P menghasilkan output fungsi f (32 bit).
   <br>
7. `des_encrypt_block(block8, subkeys)`
   ```python
   def des_encrypt_block(block8: bytes, subkeys: list) -> bytes:
       if len(block8) != 8:
           raise ValueError("Blok DES harus tepat 8 byte.")

       block = permute(int.from_bytes(block8, "big"), IP, 64)
       left = (block >> 32) & 0xFFFFFFFF
       right = block & 0xFFFFFFFF

       for i in range(16):
           left, right = right, left ^ _feistel(right, subkeys[i])

       preoutput = (right << 32) | left
       return permute(preoutput, FP, 64).to_bytes(8, "big")
   ```
   - Validasi blok harus 8 byte.
   - `permute(int.from_bytes(block8, "big"), IP, 64)`: permutasi awal, lalu bagi menjadi `left` (32 bit atas) dan
     `right` (32 bit bawah).
   - Loop 16 round Feistel: `left, right = right, left ^ f(right, subkey)`.
   - `preoutput = (right << 32) | left`: kiri-kanan ditukar (`R16 || L16`) sebelum
     permutasi akhir.
   - `permute(preoutput, FP, 64)`: permutasi akhir menghasilkan ciphertext 8 byte.
   <br>
8. `des_decrypt_block(block8, subkeys)`
   ```python
   def des_decrypt_block(block8: bytes, subkeys: list) -> bytes:
       return des_encrypt_block(block8, subkeys[::-1])
   ```
   - Dekripsi DES = enkripsi dengan subkey terbalik (K16-K1).
   - `subkeys[::-1]` membalik urutan subkey.
   <br>
9. `pad_pkcs7(data)` dan `unpad_pkcs7(data)`
   ```python
   def pad_pkcs7(data: bytes) -> bytes:
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
   ```
   - `pad_pkcs7`: hitung `pad_len` agar panjang jadi kelipatan 8, lalu tambahkan `pad_len`
     byte bernilai `pad_len`.
   - Jika panjang sudah kelipatan 8, `8 - 0 = 8` maka tetap ditambah satu blok `0x08`.
   - `unpad_pkcs7`: ambil byte terakhir sebagai `pad_len`, validasi rentang 1–8, lalu
     pastikan `pad_len` byte terakhir semuanya bernilai sama.
   <br>
10. `encrypt_message(plaintext, key8)` dan `decrypt_message(ciphertext, key8)`
   ```python
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
   ```
   - `generate_subkeys` dihitung sekali lalu dipakai untuk semua blok.
   - `pad_pkcs7` menambah padding sebelum dienkripsi.
   - Loop per 8 byte (`range(0, len, 8)`) mengenkripsi tiap blok*.
   - `decrypt_message`: dekripsi tiap blok, gabung, lalu `unpad_pkcs7`.
   <br>
### receiver.py
Penerima berperan sebagai TCP server: menerima koneksi, mendekripsi
ciphertext, menampilkan plaintext, lalu membalas terenkripsi (chat dua arah).

1. Import library
   ```python
   import argparse
   import socket
   import sys

   import des
   from common import (
       CTRL_QUIT,
       from_hex,
       key_from_config,
       parse_key,
       recv_frame,
       send_frame,
       to_hex,
   )
   ```
   - `argparse` = membaca argumen CLI.
   - `socket` = membuat koneksi/socket TCP.
   - `sys` = `sys.platform` (cek Windows/Linux) dan selesai program.
   - `des` = modul DES buatan sendiri.
   - Dari `common`: `send_frame`/`recv_frame` (protokol frame), `to_hex`/`from_hex`, `key_from_config`/`parse_key`, dan `CTRL_QUIT`.
   <br>
2. Konstanta
   ```python
   BIND_HOST = "0.0.0.0" 
   PORT = 5000              
   KEY = "KUNCI123"        
   ```
   - `0.0.0.0` = menerima koneksi dari semua interface (localhost maupun LAN).
   - `PORT` dan `KEY`harus sama dengan `sender.py`.
   <br>
3. `main()` - Validasi key
   ```python
   def main() -> int:
       args = parse_args()
       try:
           key = resolve_key(args)
       except ValueError as exc:
           print(f"[!] Key tidak valid: {exc}")
           return 1
   ```
   - Menentukan key, jika tidak valid mK cetak pesan error lalu return 1.
   <br>
4. `main()` - Membuat socket server
   ```python
       server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

       if sys.platform != "win32":
           server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       try:
           server.bind((args.host, args.port))
       except OSError as exc:
           print(f"[!] Gagal bind ke {args.host}:{args.port} -> {exc}")
           return 1
       server.listen(1)
       print(f"[*] Receiver siap. Listening di {args.host}:{args.port} ...")
       print( "[*] Key sudah tersimpan lokal (tidak dikirim ke jaringan).")

       try:
           conn, addr = server.accept()
       except KeyboardInterrupt:
           print("\n[*] Dibatalkan.")
           server.close()
           return 0

       print(f"[*] Koneksi diterima dari {addr[0]}:{addr[1]}")
   ```
   - `AF_INET` + `SOCK_STREAM` = socket TCP IPv4.
   - `bind()` menghubungkan socket ke `host:port`, jika gagal maka tampilkan pesan error dan keluar.
   - `listen(1)` = siap menerima koneksi.
   - `accept()` = menunggu sampai ada sender yang connect, lalu return `conn`.
   <br>
5. `main()` - Loop menerima & mendekripsi
   ```python
       try:
           while True:
               frame = recv_frame(conn)
               if frame is None:
                   print("[*] Koneksi ditutup oleh lawan.")
                   break

               if frame == CTRL_QUIT:
                   print("[*] Lawan mengakhiri sesi.")
                   break

               hex_ct = frame.decode("ascii", errors="replace")
               print(f"[Lawan] Ciphertext diterima : {hex_ct}")

               try:
                   plaintext = des.decrypt_message(from_hex(hex_ct), key)
                   print(f"[Lawan] Plaintext (dekripsi): {plaintext.decode('utf-8', errors='replace')}")
               except (ValueError, UnicodeDecodeError) as exc:
                   print(f"[!] Gagal dekripsi pesan: {exc}")
                   # tetap lanjut agar sesi tidak putus karena satu pesan rusak
                   continue
   ```
   - `recv_frame(conn)`: baca satu frame utuh, `None` = lawan menutup koneksi.
   - `frame == CTRL_QUIT`: lawan minta berhenti, maka keluar dari loop.
   - Tampilkan ciphertext hex yang diterima.
   - Jika dekripsi gagal, pesan error ditampilkan dan sesi tetap berjalan (`continue`).
   <br>
6. `main()` - Mengirim balasan
   ```python
               try:
                   reply = input("[Ketik balasan Anda] > ")
               except EOFError:
                   print("\n[*] Tidak ada input lagi. Menutup sesi.")
                   send_frame(conn, CTRL_QUIT)
                   break

               if reply == "/quit":
                   send_frame(conn, CTRL_QUIT)
                   print("[*] Mengakhiri sesi...")
                   break

               reply_ct = des.encrypt_message(reply.encode("utf-8"), key)
               print(f"[Saya] Plaintext  : {reply}")
               print(f"[Saya] Ciphertext : {to_hex(reply_ct)}")
               send_frame(conn, to_hex(reply_ct).encode("ascii"))
               print("[Saya] Terkirim.")
   ```
   - `input()` menerima balasan user, jika `EOFError` (tidak ada input) maka kirim `QUIT` dan keluar.
   - jika `/quit`, maka kirim `QUIT` ke lawan lalu keluar.
   - Balasan di-encode UTF-8 `encrypt_message` diubah ke hex dan dikirim sebagai frame.
   <br>
7. `main()` - Penanganan interrupt & penutupan
   ```python
       except KeyboardInterrupt:
           print("\n[*] Dihentikan pengguna.")
       finally:
           conn.close()
           server.close()

       print("[*] Receiver berhenti.")
       return 0
   ```
   - `KeyboardInterrupt` (Ctrl+C).
   - `finally`: socket koneksi dan socket server selalu ditutup.
   <br>
8. Titik masuk program
    ```python
    if __name__ == "__main__":
        sys.exit(main())
    ```
    - Menjalankan `main()` hanya jika file dieksekusi langsung, lalu keluar dengan exit code-nya.
    <br>
### sender.py
Pengirim berperan sebagai TCP client: terhubung ke receiver,
mengenkripsi input user, mengirim ciphertext, lalu menerima dan mendekripsi balasan.

1. Import library
   ```python
   import socket
   import sys

   import des
   from common import (
       send_frame,
       recv_frame,
       to_hex,
       from_hex,
       key_from_config,
       CTRL_QUIT,
   )
   ```
   - Sama seperti receiver, tambahkan `send_frame` karena sender lebih banyak mengirim.
   <br>
2. Konstanta
   ```python
   TARGET_HOST = "127.0.0.1" 
   PORT = 5000                
   KEY = "KUNCI123"          
   ```
   - `TARGET_HOST` = alamat receiver yang dituju, `127.0.0.1` untuk satu device,
     ganti ke IP `192.168.56.101` untuk terhubung ke VM.
   - `PORT` dan `KEY` harus sama dengan `receiver.py`.
   <br>
3. `main()` - Validasi key & menghubungkan ke receiver
   ```python
   def main() -> int:
       try:
           key = key_from_config(KEY)
       except ValueError as exc:
           print(f"[!] Key tidak valid: {exc}")
           return 1

       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       try:
           sock.connect((TARGET_HOST, PORT))
       except OSError as exc:
           print(f"[!] Tidak bisa terhubung ke {TARGET_HOST}:{PORT} -> {exc}")
           return 1

       print(f"[*] Terhubung ke receiver {TARGET_HOST}:{PORT}")
       print( "[*] Key sudah tersimpan lokal (tidak dikirim ke jaringan).")
       print( "[*] Ketik pesan lalu Enter. Ketik /quit untuk mengakhiri.\n")
   ```
   - Validasi key terlebih dahulu (keluar bila tidak valid).
   - `sock.connect((TARGET_HOST, PORT))` menghubungkan ke receiver (nilai dari konstanta), jika gagal maka tampilkan error dan keluar.
   - Bila receiver belum dijalankan, tampilkan `[!] Tidak bisa terhubung ...`.
   <br>
4. `main()` - Loop mengirim pesan terenkripsi
   ```python
       try:
           while True:
               try:
                   message = input("[Ketik pesan Anda] > ")
               except EOFError:
                   print("\n[*] Tidak ada input lagi. Menutup sesi.")
                   send_frame(sock, CTRL_QUIT)
                   break

               if message == "/quit":
                   send_frame(sock, CTRL_QUIT)
                   print("[*] Mengakhiri sesi...")
                   break

               ciphertext = des.encrypt_message(message.encode("utf-8"), key)
               print(f"[Saya] Plaintext  : {message}")
               print(f"[Saya] Ciphertext : {to_hex(ciphertext)}")
               send_frame(sock, to_hex(ciphertext).encode("ascii"))
               print("[Saya] Terkirim.")
   ```
   - `input()` menerima pesan, jika `EOFError` maka kirim `QUIT` dan keluar.
   - Jika `/quit` maka kirim `QUIT` dan keluar.
   - Pesan di-encode UTF-8, maka `encrypt_message` dan `to_hex` akan dikirim sebagai frame.
   - Sender mengirim pesan lebih dulu.
   <br>
5. `main()` - Menerima & mendekripsi balasan
   ```python
               frame = recv_frame(sock)
               if frame is None:
                   print("[*] Lawan menutup koneksi.")
                   break
               if frame == CTRL_QUIT:
                   print("[*] Lawan mengakhiri sesi.")
                   break

               print(f"[Lawan] Ciphertext diterima : {frame.decode('ascii', errors='replace')}")
               try:
                   plaintext = des.decrypt_message(from_hex(frame.decode("ascii")), key)
                   print(f"[Lawan] Plaintext (dekripsi): {plaintext.decode('utf-8', errors='replace')}")
               except (ValueError, UnicodeDecodeError) as exc:
                   print(f"[!] Gagal dekripsi pesan: {exc}")
   ```
   - Setelah mengirim, sender menunggu balasan `recv_frame`.
   - Jika `None` artinya lawan menutup, jika `CTRL_QUIT` artinya lawan mengakhiri sesi.
   - Balasan ditampilkan sebagai ciphertext hex, lalu didekripsi dan ditampilkan plaintext-nya.
   <br>
6. `main()` - Penanganan interrupt & penutupan
   ```python
       except KeyboardInterrupt:
           print("\n[*] Dihentikan pengguna.")
           try:
               send_frame(sock, CTRL_QUIT)
           except OSError:
               pass
       finally:
           sock.close()

       print("[*] Sender berhenti.")
       return 0
   ```
   - Ctrl+C mengirim `QUIT` agar lawan tahu, lalu keluar.
   - `finally` menutup socket pengirim.
   <br>
7. Titik masuk program
   ```python
   if __name__ == "__main__":
       sys.exit(main())
   ```
   - Menjalankan `main()` lalu keluar dengan exit code-nya.
   <br>
