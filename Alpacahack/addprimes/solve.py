from sage.all import *
from Crypto.Util.number import *
from pwn import *

def attack(N, e, phi, c):
    """
    Computes possible plaintexts when e is not coprime with Euler's totient.
    More information: Shumow D., "Incorrectly Generated RSA Keys: How To Recover Lost Plaintexts"
    :param N: the modulus
    :param e: the public exponent
    :param phi: Euler's totient for the modulus
    :param c: the ciphertext
    :return: a generator generating possible plaintexts for c
    """
    assert phi % e == 0, "Public exponent must divide Euler's totient"
    if gcd(phi // e, e) == 1:
        assert is_prime(e), "Public exponent must be prime"
        phi //= e
        # Finding multiplicative generator of subgroup with order e elements (Algorithm 1).
        g = 1
        gE = 1
        while gE == 1:
            g += 1
            gE = int(pow(g, phi, N))

        # Finding possible plaintexts (Algorithm 2).
        d = int(pow(e, -1, phi))
        a = int(pow(c, d, N))
        l = gE
        for i in range(e):
            x = a * l % N
            l = l * gE % N
            yield x
        
while True:
    conn=remote('34.170.146.252',20209)
    # conn=process(['sage','chall.sage'])
    q=conn.recvlines(2)
    n=int(q[0].split(b': ')[1])
    e=37
    a=2**512
    conn.sendline(str(pow(a,e,n)))
    q=conn.recvline()
    m=int(q.split(b'plaintext: ')[1])
    print(gcd(abs(m-a),n))

    if gcd(abs(m-a),n)<n and gcd(abs(m-a),n)>1:
        print('Found it!!')
        p=gcd(abs(m-a),n)
        q=n//p
        q1=conn.recvline()
        ct=int(q1.split(b'encrypted flag: ')[1])
        for i in attack(n,e,(p-1)*(q-1),ct):
            print(long_to_bytes(int(i)))
        break
    conn.close()