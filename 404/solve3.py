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

# conn = process(['python3', 'chall3.py'])
conn=remote('challenge.404ctf.fr', 10003)

res = []
mat = []
req = 0
for k in range(5):
    ss = []
    ts = []
    ys = []
    for i in range(63):
        req += 1
        if req == 300:
            break
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
    for i in range(len(ys)):
        y = ys[i]
        dec = sum([xi * ei for xi, ei in zip(y, Ei)])
        dec -= K2(ss[i]) * C + K2(ts[i]) * D
        part_dec.append(dec)
            
    # conn.sendline(b'4')
    # conn.recvuntil(b'>>> ')
    # q = conn.recvline().strip()
    # a = loads(q)
    # x = vector(K2, a["x"])
    ress = [part_dec[0]*inverse(i+ys[0][-1], n) for i in range(0, 256)]
    for j in range(1,len(ys)):
        ress1 = [part_dec[j]*inverse(i+ys[j][-1], n) for i in range(0, 256)]
        for g in ress1:
            if g in ress:
                print(f"Found i: {j} {ress1.index(g)}")
                if j == 1:
                    mat.append(ys[0])
                    res.append(ress.index(g))
                mat.append(ys[j])
                res.append(ress1.index(g))
                
    print(res)

mat = matrix(K2, mat)
res = matrix(K2, res)
sol = mat.solve_right(res.T)
sol = sol.T
print(sol)
sol = list(list(sol)[0])
sol[-1] = 1
conn.sendline(b'3')
conn.sendline(str(sol))
conn.interactive()