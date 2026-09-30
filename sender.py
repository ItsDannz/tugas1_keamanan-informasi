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

TARGET_HOST = "127.0.0.1"
PORT = 5000
KEY = "KUNCI123"

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

if __name__ == "__main__":
    sys.exit(main())
