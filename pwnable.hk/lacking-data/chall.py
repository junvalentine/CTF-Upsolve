import os
import hashlib
from math import prod
from secrets import randbelow
from Crypto.Cipher import AES
from Crypto.Util.number import getPrime
from Crypto.Util.Padding import pad


def int_sha256(value: int) -> int:
    return int.from_bytes(hashlib.sha256(value.to_bytes(32, "little")).digest(), "little")


def setup() -> tuple[int, int, int, int]:
    p = getPrime(256)
    a, k1, k2 = [randbelow(p) for _ in range(3)]
    return (p, a, k1, k2)


def keygen(subset: set[int], secret_key: tuple[int, int, int, int]) -> tuple[int, int]:
    p, a, k1, k2 = secret_key
    assert all(0 <= i < 1337 for i in subset)

    r, t = [randbelow(p) for _ in range(2)]

    f = prod(a + int_sha256(i) for i in subset)

    s = pow(k1, -1, p) * (pow(f, -1, p) - 3 * k2 * r) % p
    u1 = (r + k1 * t) % p
    u2 = (s - 3 * k2 * t) % p

    return (u1, u2)


def main():
    FLAG = os.getenv("FLAG") or "bsideshk{placeholder_flag}"
    secret_key = setup()

    derived_key = hashlib.sha256(str(secret_key).encode()).digest()[:16]
    cipher = AES.new(derived_key, AES.MODE_CBC)

    enc_flag = cipher.iv + cipher.encrypt(pad(FLAG.encode(), 16))
    print(f"Encrypted flag (hex): {enc_flag.hex()}")

    for _ in range(5):
        subset = set(map(int, input("subset: ").split()))
        print(*keygen(subset, secret_key))
    print(secret_key)  # For testing purposes only
    f = prod(secret_key[1] + int_sha256(i) for i in [0, 1, 2, 3, 4])

if __name__ == "__main__":
    main()
