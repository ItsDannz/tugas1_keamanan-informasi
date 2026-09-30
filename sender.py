import argparse
import socket
import sys

import des
from common import (
    send_frame,
    recv_frame,
    to_hex,
    from_hex,
    parse_key,
    key_from_config,
    CTRL_QUIT,
)

TARGET_HOST = "127.0.0.1"
PORT = 5000
KEY = "KUNCI123"

def parse_args():
    p = argparse.ArgumentParser(
        description="Sender DES (TCP client). Semua argumen opsional; "
    )
    p.add_argument(
        "--host", default=TARGET_HOST, help=f"Alamat receiver (default: {TARGET_HOST})"
    )
    p.add_argument(
        "--port", type=int, default=PORT, help=f"Port (default: {PORT})"
    )
    p.add_argument(
        "--key", help='Override key 8 karakter ASCII, mis. "KUNCI123"'
    )
    p.add_argument(
        "--key-hex", help="Override key 16 digit hex, mis. 133457799BBCDFF1"
    )
    return p.parse_args()

def resolve_key(args):
    if args.key is None and args.key_hex is None:
        return key_from_config(KEY)
    return parse_key(args.key, args.key_hex)


def main() -> int:
    args = parse_args()
    try:
        key = resolve_key(args)
    except ValueError as exc:
        print(f"[!] Key tidak valid: {exc}")
        return 1

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((args.host, args.port))
    except OSError as exc:
        print(f"[!] Tidak bisa terhubung ke {args.host}:{args.port} -> {exc}")
        return 1

    print(f"[*] Terhubung ke receiver {args.host}:{args.port}")
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
