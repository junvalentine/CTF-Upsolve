from sage.all import *
from pwn import *
from json import loads,dumps
from Crypto.Util.number import inverse
from tqdm import tqdm
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
K = GF(p)
a = K(0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC)
b = K(0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B)
E = EllipticCurve(K, (a, b))
E.set_order(0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551 * 0x1)

K2 = GF(E.order())
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# conn = process(['python3', 'chall2.py'])
conn=remote('challenge.404ctf.fr', 10002)

res = []
mat = []
for k in range(5):
    ss = []
    ts = []
    ys = []
    for i in range(63):
        conn.sendline(b'1')
        conn.recvuntil(b'>>> ')
        q = conn.recvline().strip()
        a = loads(q)
        g = a["g"]
        ss.append(a["sx"])
        ts.append(a["tx"])
        ys.append(a["y"])

    conn.sendline(b'2')
    conn.recvuntil(b'>>> ')
    q = conn.recvline().strip()
    a = loads(q)
    C = a["C"]
    D = a["D"]
    Ei = a["Ei"]
    C = E(C[0], C[1])
    D = E(D[0], D[1])
    Ei = [E(Ei[i][0], Ei[i][1]) for i in range(256)]
    
    part_dec = []
    for i in range(63):
        y = ys[i]
        dec = sum([xi * ei for xi, ei in zip(y, Ei)])
        dec -= K2(ss[i]) * C + K2(ts[i]) * D
        part_dec.append(dec)
            
    # conn.sendline(b'4')
    # conn.recvuntil(b'>>> ')
    # q = conn.recvline().strip()
    # a = loads(q)
    # x = vector(K2, a["x"])
    
    for i in range(1, 256):
        ress = [part_dec[0]*inverse(i, n)*j for j in range(256)]
        if all([r in ress for r in part_dec]):
            print(f"Found i: {i}")
            res.append(i)
            mat.append(ys[0])
            for o in range(1,63):
                mat.append(ys[o])
                res.append(ress.index(part_dec[o]))
            break
    print(res)

mat = matrix(K2, mat)
res = matrix(K2, res)
sol = mat.solve_right(res.T)
sol = sol.T
conn.sendline(b'3')
conn.sendline(str(list(list(sol)[0])))
conn.interactive()