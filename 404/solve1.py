from sage.all import *
from pwn import *
from json import loads

p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
K = GF(p)
a = K(0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC)
b = K(0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B)
E = EllipticCurve(K, (a, b))
E.set_order(0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551 * 0x1)

K2 = GF(E.order())

# conn = process(['python3', 'chall1.py'])
conn=remote('challenge.404ctf.fr',10001)

ss = []
ts = []
ys = []
for i in range(257):
    conn.sendline(b'1')
    conn.recvuntil(b'>>> ')
    q = conn.recvline().strip()
    a = loads(q)
    g = a["g"]
    ss.append(a["sx"])
    ts.append(a["tx"])
    ys.append(a["y"])

ss = vector(K2, ss)
ts = vector(K2, ts)
ys = matrix(K2, ys)
s = ys.solve_right(ss)
t = ys.solve_right(ts)
print(s[:5],t[:5])

conn.sendline(b'2')
conn.recvuntil(b'>>> ')
q = conn.recvline().strip()
a = loads(q)
C = a["C"]
D = a["D"]
Ei = a["Ei"]
C = E(C[0], C[1])
D = E(D[0], D[1])
print(C,D)
sol = []
for i in range(256):
    e = E(Ei[i][0], Ei[i][1])
    ee = C * s[i] + D * t[i]
    if e == ee:
        sol.append(0)
    else:
        sol.append(1)
print(sol)  
conn.sendline(b'3')
conn.sendline(str(sol).encode())

conn.interactive()