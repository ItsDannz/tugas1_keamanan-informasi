import struct

MAX_PAYLOAD = 1 << 20

CTRL_QUIT = b"QUIT"

def send_frame(sock, payload: bytes) -> None:
    header = struct.pack(">I", len(payload))
    sock.sendall(header + payload)

def _recv_exact(sock, n: int):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return bytes(buf)

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

def to_hex(data: bytes) -> str:
    return data.hex().upper()

def from_hex(text: str) -> bytes:
    return bytes.fromhex(text)

def key_from_config(raw) -> bytes:
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
