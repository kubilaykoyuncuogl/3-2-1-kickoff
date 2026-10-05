"""index.sqlite → index.enc (AES-256-GCM, 1 MiB parçalar, her parça ayrı nonce + tag).

Anahtar: ortam değişkeni KICKOFF_INDEX_KEY (64 hex = 32 byte). Üretmek için:
    python tools/encrypt_index.py --gen-key
Şifrele:  python tools/encrypt_index.py --in data/index/index.sqlite --out data/index/index.enc
Çöz:      python tools/encrypt_index.py --decrypt --in data/index/index.enc --out /dev/shm/index.sqlite
Servis (server/index_service.py) dosyayı diske yazmadan belleğe çözer.

Dosya biçimi: b"K3OF" | ver(1) | chunk_len(4, BE) | [nonce(12) | ciphertext+tag(chunk_len+16)]* | son parça kısa olabilir.
AAD = başlık (sürüm + chunk_len), böylece başlık da bütünlük altında.
"""
import argparse, os, secrets, struct, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"K3OF"; VER = 1; CHUNK = 1 << 20

def key_from_env() -> bytes:
    k = os.environ.get("KICKOFF_INDEX_KEY", "")
    if len(k) != 64: sys.exit("KICKOFF_INDEX_KEY yok ya da 64 hex değil (python tools/encrypt_index.py --gen-key)")
    return bytes.fromhex(k)

def encrypt_file(src: str, dst: str, key: bytes) -> None:
    aes = AESGCM(key); header = MAGIC + bytes([VER]) + struct.pack(">I", CHUNK)
    with open(src, "rb") as f, open(dst, "wb") as o:
        o.write(header)
        while chunk := f.read(CHUNK):
            nonce = secrets.token_bytes(12)
            o.write(nonce + aes.encrypt(nonce, chunk, header))

def decrypt_bytes(src: str, key: bytes) -> bytes:
    aes = AESGCM(key); out = bytearray()
    with open(src, "rb") as f:
        header = f.read(9)
        if header[:4] != MAGIC or header[4] != VER: raise ValueError("index.enc biçimi tanınmadı")
        clen = struct.unpack(">I", header[5:9])[0]
        while True:
            nonce = f.read(12)
            if not nonce: break
            ct = f.read(clen + 16)
            out += aes.decrypt(nonce, ct, header)   # tag uyuşmazsa InvalidTag → kurcalanmış dosya
    return bytes(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen-key", action="store_true"); ap.add_argument("--decrypt", action="store_true")
    ap.add_argument("--in", dest="inp"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.gen_key:
        print(secrets.token_hex(32)); sys.exit()
    key = key_from_env()
    if a.decrypt:
        with open(a.out, "wb") as o: o.write(decrypt_bytes(a.inp, key))
    else:
        encrypt_file(a.inp, a.out, key)
    print("ok", a.out, os.path.getsize(a.out) // 1_000_000, "MB")
