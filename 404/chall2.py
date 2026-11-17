from sage.all import *
from Crypto.Random.random import randrange
import json
import os

FLAG = os.getenv("FLAG")

# NIST P256
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
K = GF(p)
a = K(0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc)
b = K(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
E = EllipticCurve(K, (a, b))
E.set_order(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551 * 0x1)

K2 = GF(E.order())

INSTANCE_SIZE = 256
INSTANCE_TRIES = 64
TRIES = 7

# According to https://eprint.iacr.org/2015/608.pdf
def setup():
    g, h = E.random_element(), E.random_element()
    s = vector(K2, [K2.random_element() for _ in range(INSTANCE_SIZE)])
    t = vector(K2, [K2.random_element() for _ in range(INSTANCE_SIZE)])

    hi = []
    for si, ti in zip(s, t):
        hi.append(g * si + h * ti)

    return g, h, hi, s, t


def keygen(s, t, x):
    return s * x, t * x


def encrypt(g, h, hi, y):
    r = K2.random_element()
    alpha = K2.random_element()
    alpha_g = alpha * g
    C = r * g
    D = r * h
    Ei = []
    for yi, hi_element in zip(y, hi):
        Ei.append(yi * alpha_g + r * hi_element)

    return C, D, Ei

# Good luck :)
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
    random_vector = None
    ciphertext = None

    print("What should I do ?\n\t1 Get a key for a vector\n\t2 Get an encrypted vector\n\t3 Check\n")
    rq = 0
    while rq < TRIES * INSTANCE_TRIES:
        action = input(">>> ")
        rq += 1

        if action == "1":
            y = get_random_vector()
            sx, tx = keygen(s, t, y)
            print(json.dumps({"g": encode_vector(list(g)), "sx": int(sx), "tx": int(tx), "y": encode_vector(y)}))
        elif action == "4":
            print(json.dumps({"x": encode_vector(random_vector)}))
        elif action == "2":
            if random_vector is None:
                random_vector = get_random_vector()
            if ciphertext is None:
                ciphertext = encrypt(g, h, hi, random_vector)

            # Convert to integers so that we can dump it
            C_encoded, D_encoded, Ei_encoded = encode_ct(*ciphertext)
            print(
                json.dumps({"C": C_encoded, "D": D_encoded, "Ei": Ei_encoded})
            )

        elif random_vector is not None and action == "3":
            vector = json.loads(input("What is your guess ?\n>>> "))
            if encode_vector(vector) == encode_vector(random_vector):
                print(f"Congratz ! Here is your flag {FLAG}")
            else:
                print("Nope :/", random_vector)
                exit(1337)

        else:
            print("Invalid action")
            exit(1234)


        # re-key
        if rq and rq % INSTANCE_TRIES == 0:
            print("Please wait, re-keying...")
            g, h, hi, s, t = setup()
            ciphertext = None