from Crypto.Util.number import getPrime, getRandomRange
from math import floor, isqrt
import json, random, os
from sage.all import *
from pwn import *

a=int('9'*4300)
limit=a+1
res=0
cur = 2**513
fl=''
conn=remote('zkpof.chal.hitconctf.com',11111)
exec(conn.recvline())
print(n)

res=0
cur = 2**513
rand = random.Random(1337)
for i in range(311):
    z = rand.randrange(2, n)
    mid = (res+cur)//2
    e=-limit//mid
    conn.sendline(str(e))
    q=conn.recvline()
    if b'Error: Exceeds' in q:
        res=mid
        fl+='1'
    else:
        cur=mid
        fl+='0'
    print(fl)

b = -int(fl, 2) << (513 - len(fl))

# solve x^2 - (p + q)x + n = 0
delta = b**2 - 4*n
assert delta >= 0
sqrt_delta = isqrt(delta)
r1 = (-b + sqrt_delta) // 2

PR = PolynomialRing(Zmod(n), 'x')
x = PR.gen()
shift = r1.nbits() - 300
f = x + ((r1 >> shift) << shift)
rs = f.small_roots(X=2**shift, beta=0.5)
pp= int((r1 >> shift) << shift) + int(rs[0])

print(rs)
assert n % pp == 0
q = n // pp
phi = (pp - 1) * (q - 1)
conn.recvline()
for _ in range(floor(13.37)):
    z = rand.randrange(2, n)
    r = getRandomRange(0, A)
    x = pow(z, r, n)
    conn.sendline(str(x))
    e = int(conn.recvline().split(b'e = ')[1].strip().decode())
    print(e)
    y = r + (n - phi) * e
    conn.sendline(str(y))
    conn.recvline()
conn.interactive()

