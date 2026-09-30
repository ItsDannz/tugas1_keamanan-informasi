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

BIND_HOST = "0.0.0.0"
PORT = 5000
KEY = "KUNCI123"

def parse_args():
    p = argparse.ArgumentParser(
        description="Receiver DES (TCP server). Semua argumen opsional; "
                    "default di-hardcode di bagian atas file ini."
    )
    p.add_argument("--host", default=BIND_HOST,
                   help=f"Alamat bind (default: {BIND_HOST})")
    p.add_argument("--port", type=int, default=PORT,
                   help=f"Port (default: {PORT})")
    p.add_argument("--key", help='Override key 8 karakter ASCII, mis. "KUNCI123"')
    p.add_argument("--key-hex", help="Override key 16 digit hex, mis. 133457799BBCDFF1")
    return p.parse_args()


def resolve_key(args):
    """Tentukan key: prioritas argumen CLI, fallback ke KEY yang di-hardcode."""
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
