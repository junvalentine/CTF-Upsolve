def Babai_closest_vector(B, target):
    # Babai's Nearest Plane algorithm
    M = B.LLL()
    G = M.gram_schmidt()[0]
    small = target
    for _ in range(1):
        for i in reversed(range(M.nrows())):
            c = ((small * G[i]) / (G[i] * G[i])).round()
            small -= M[i] * c
    return target - small

import hashlib
import ecdsa
from sage.all import *
from Crypto.Util.number import *
from Crypto.Cipher import AES

s = 98064531907276862129345013436610988187051831712632166876574510656675679745081
r = 9821122129422509893435671316433203251343263825232865092134497361752993786340
curve = ecdsa.NIST256p.generator
order = int(curve.order())
cipher = b'\xf3#\xff\x17\xdf\xbb\xc0\xc6v\x1bg\xc7\x8a6\xf2\xdf~\x12\xd8]\xc5\x02Ot\x99\x9f\xf7\xf3\x98\xbc\x045\x08\xfb\xce1@e\xbcg[I\xd1\xbf\xf8\xea\n-'
msg = b'welcome to n1ctf2023!'
msg_hash = bytes_to_long(hashlib.sha256(msg).digest())
msg_bin = int(bin(msg_hash)[2:].zfill(256)[:128],2)

# msg_bin*2**128*s + d_high*s= msg_hash + r*(d_high*2**128 + d_low) [ord]
const=(msg_bin*2^128*s-msg_hash)%order

BH = 2^128
BL = 2^128
mat=Matrix(QQ,[
    [1/BH, 0,    r*2^128-s],
    [0,    1/BL, r],
    [0,    0,   -order]
    ])

Y = vector(QQ, [0.8, 0.8,const])
W = Babai_closest_vector(mat, Y)
print(W)
print((1/2**128) * 2**128)
print(2**128)
print(factor(113427455640312808561480914824870232064))
H = abs(int(W[0]*BH))
L = abs(int(W[1]*BL))

d = int(2**128*H + L)
# correct : d = 114848009668899858113932463053239179798180491260873213931636897786613068143546

key = long_to_bytes(d)

if len(key) == 32:
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        flag = cipher.decrypt(cipher)
        if b'n1ctf' in flag:
            print(flag)
            exit()
    except:
        pass