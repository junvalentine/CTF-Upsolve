from sage.all import *
from Crypto.Util.number import *
from pwn import *
import json

# smooth prime, actually N=p is enough, no need for q
p, q = 22244217765237114366547569852803319182174004326418805776349266336372222494461901759 , 47005465824747030107982847070762976086530969740124896305958856303785233428334266379
N=p*q
ordd= (p-1)*(q-1)

h2= p+1

#dlnproof forge
from common import *
from dlnproof import *

f=1
while f:
    t= random.randint(1,ordd)
    ts= [t for i in range(32)]
    alpha= pow(h2,t,N)
    a = long_to_bytes(alpha)
    beta = bytes_to_long(a + b',' + a)
    h1= alpha*inverse(beta,N) % N

    try:
        K=Zmod(N)
        x=discrete_log(K(h2),K(h1),Integer((p-1)*(q-1)))
        if x==0:
            continue
    except exception as e:
        continue

    for l in range(32):
        alpha1=[alpha for i in range (l)]+[beta for i in range(32-l)] 
        msg = [h2, h1, N] + alpha1
        c = long_to_bin(SHA512_256i(msg))[:32]
        if sum(c)== 32-l:
            print('found')
            f=0
            for i in range(len(c)):
                if c[i]==1:
                    alpha1[i]=beta
                else:
                    alpha1[i]=alpha
            print(verify(h2, h1, N, alpha1, ts))
            break

K=Zmod(N)
x=discrete_log(K(h2),K(h1),Integer((p-1)*(q-1)))
print(x)
assert pow(h1,x,N)==h2

def getDLNProof(h1, h2, x, phi, N):
    h1 = h1 % N
    h2 = h2 % N
    assert pow(h1, x, N) == h2
    a = [random.randint(1, phi - 1) for _ in range(Iterations)]
    alpha = [pow(h1, a[i], N) for i in range(Iterations)]
    msg = [h1, h2, N] + alpha
    c = long_to_bin(SHA512_256i(msg))[:Iterations]
    t = [(a[i] + c[i] * x) % phi for i in range(Iterations)]
    return (alpha, t)

alpha,t = getDLNProof(h1,h2,x,ordd,N)
print(verify(h1, h2, N, alpha, t))

# conn = process(['python3','server.py'])
conn=remote('183.91.11.30',int(1337))

alpha=[int(i) for i in alpha]
t=[int(i) for i in t]
alpha1=[int(i) for i in alpha1]
ts=[int(i) for i in ts]
payload = {"NTildeB": int(N), "h1B": int(h1), "h2B": int(h2), "dlnproof": [(alpha,t),(alpha1,ts)]}
conn.sendline(json.dumps(payload))

from ecc import *
conn.sendline(G.to_bytes().hex())

a= conn.recvuntil(b'Round2Msg =').split(b'Round2Msg =')[0].split(b'Round1Msg = ')[1]
a=json.loads(a)['proofA']['Z']

K = GF(p)
print(K(a).log(K(h1)))
print(long_to_bytes(int(K(a).log(K(h1)))))
