import socket
import sys

import des
from common import (
    CTRL_QUIT,
    from_hex,
    key_from_config,
    recv_frame,
    send_frame,
    to_hex,
)

BIND_HOST = "0.0.0.0"
PORT = 5000
KEY = "KUNCI123"

def main() -> int:
    try:
        key = key_from_config(KEY)
    except ValueError as exc:
        print(f"[!] Key tidak valid: {exc}")
        return 1

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sys.platform != "win32":
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((BIND_HOST, PORT))
    except OSError as exc:
        print(f"[!] Gagal bind ke {BIND_HOST}:{PORT} -> {exc}")
        return 1
    server.listen(1)
    print(f"[*] Receiver siap. Listening di {BIND_HOST}:{PORT} ...")
    print( "[*] Key sudah tersimpan lokal (tidak dikirim ke jaringan).")

    try:
        conn, addr = server.accept()
    except KeyboardInterrupt:
        print("\n[*] Dibatalkan.")
        server.close()
        return 0

    print(f"[*] Koneksi diterima dari {addr[0]}:{addr[1]}")

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
                continue

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
    except KeyboardInterrupt:
        print("\n[*] Dihentikan pengguna.")
    finally:
        conn.close()
        server.close()

    print("[*] Receiver berhenti.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
