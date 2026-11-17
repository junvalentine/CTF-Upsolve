from sage.all import *
import json
import os
from Crypto.Random.random import randrange

FLAG = os.getenv("FLAG")

# NIST P256
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
K = GF(p)
a = K(0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC)
b = K(0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B)
E = EllipticCurve(K, (a, b))
E.set_order(0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551 * 0x1)

K2 = GF(E.order())

INSTANCE_SIZE = 256
TRIES = 300


# According to https://eprint.iacr.org/2015/608.pdf
def setup():
    g, h = E.random_element(), E.random_element()
    s = vector(K2, [K2.random_element() for _ in range(INSTANCE_SIZE)])
    t = vector(K2, [K2.random_element() for _ in range(INSTANCE_SIZE)])

    hi = []
    for si, ti in zip(s, t):
        hi.append(si * g + ti * h)

    return g, h, hi, s, t


def keygen(s, t, x):
    return s * x, t * x


def encrypt(g, h, hi, y):
    r = K2.random_element()
    C = r * g
    D = r * h
    Ei = []
    for yi, hi_element in zip(y, hi):
        Ei.append(yi * g + r * hi_element)

    return C, D, Ei


def decrypt(g, x, sx, tx, C, D, Ei, log_table=None):
    partial_decrypt = sum([xi * ei for xi, ei in zip(x, Ei)])
    partial_decrypt -= K2(sx) * C + K2(tx) * D

    if log_table:
        return log_table[partial_decrypt]
    else:
        return partial_decrypt.log(g)


def get_random_vector():
    return vector(K2, [randrange(0, 2) for _ in range(INSTANCE_SIZE)])


# Convenient functions to print to json
# format some sagemath types
def encode_vector(v):
    return [int(e) for e in v]


def encode_ct(C, D, Ei):
    return (
        encode_vector(list(C)),
        encode_vector(list(D)),
        [encode_vector(list(ei)) for ei in Ei],
    )


if __name__ == "__main__":
    g, h, hi, s, t = setup()
    ciphertext = None
    random_vector = None

    rq = 0
    while rq < TRIES:
        action = input(
            "What should I do ?\n\t1 Get a key for a vector\n\t2 Get an encrypted vector\n\t3 Check\n>>> "
        )
        rq += 1

        if action == "1":
            y = get_random_vector()
            sx, tx = keygen(s, t, y)
            print(json.dumps({"g": encode_vector(list(g)), "sx": int(sx), "tx": int(tx), "y": encode_vector(y)}))
        # elif action == "4":
        #     print(s[:5], t[:5])
        elif ciphertext is None and action == "2":
            random_vector = get_random_vector()

            ciphertext = encrypt(g, h, hi, random_vector)

            # Convert to integers so that we can dump it
            C_encoded, D_encoded, Ei_encoded = encode_ct(*ciphertext)
            print(
                json.dumps({"C": C_encoded, "D": D_encoded, "Ei": Ei_encoded})
            )

        elif ciphertext is not None and action == "3":
            vector = json.loads(input("What is your guess ?\n>>> "))
            
            if encode_vector(vector) == encode_vector(random_vector):
                print(f"Congratz ! Here is your flag {FLAG}")
            else:
                print("Nope :/")
                exit(1337)

        else:
            print("Invalid action")
            exit(1234)