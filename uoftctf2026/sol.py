
from hashlib import sha256

def cvp(B, t):
    t = vector(ZZ, t)
    B = B.LLL()
    S = B[-1].norm().round()+1
    L = block_matrix([
        [B,         0],
        [matrix(t), S]
    ])
    for v in L.LLL():
        if abs(v[-1]) == S:
            return t - v[:-1]*sign(v[-1])
    raise ValueError('cvp failed?!')

def h(m):
    return bytes_to_long(sha256(m).digest())

from Crypto.Cipher import AES
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
K = GF(p)
a = K(0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc)
b = K(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
E = EllipticCurve(K, (a, b))
G = E(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296, 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
E.set_order(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551 * 0x1)
order = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
alphabet = string.ascii_letters + string.digits

while True:
    t = 67
    
    res= []
    msgs= []
    for i in range(t):
        msg = random.choices(alphabet, k=16)
        msg = ''.join(msg).encode()
        msgs.append(msg.hex())
        res.append(h(msg))
        
    target = 2**256 - 666    
    mat = []
    for i in range(len(res)):
        row = [0]*i + [1] + [0]*(len(res)-i-1) + [res[i]]
        mat.append(row)
    
    mat.append([0]*len(res) + [2**256])
    mat = matrix(ZZ, mat)

    tar = vector(ZZ, [10]*len(res) + [target])
    ress = cvp(mat, tar)
    
    a = [x*y for x,y in zip(ress[:-1], res)]
    if all(x>=0 for x in ress[:-1]) and target - sum(a)%(2**256) == sum(ress[:-1]) - 666:
        print(msgs)
        break

msg=['6572314d52324664704e5269754f4c4b', '475162516d42673369594d326c646148', '454b387364494d76704e31665a443647', '6c434461364d75336d4a574b31577841', '326734363470303254766e7131463865', '41487631556a416b6e674f584e617473', '777463686a52713447723471394e4c46', '7664366f764d6f774152343953575742', '703230524136396866345565705a397a', '6e654475483879565256637632593955', '6d4c516d504849576a42516866554661', '6d64706565454f6e654d746b516b3741', '30426e504e566d5a57556b4a4e495869', '34334252766a7437556841674939544f', '46637959753977347778675a627a7a47', '4655467a6475763434426551686c4e32', '4b744c7a77366f393949394e654b7044', '626c7568634c4d746939637377373270', '6233663737595a715332564c68334854', '4135686c3432344c7634386d78684172', '67575359516672336948346463434445', '4c64503863616f774a6767734b636342', '733464706150657a4e69377442317775', '566d41775339326f4b4a677362495047', '7867767042463446665a6b5045767970', '336632336159484c7535665436584655', '6f61614c385a5a5a6c6d31436150534a', '686b63573638383848756a33736c795a', '44434c5750325534703257736238586d', '56355458524d4c346a33575a50737269', '6157794c67544237306b5a5849684367', '774f656a574c6b556d5968375a6f514d', '33496f52786e524a596a37355a494e77', '61414b4f6a4b6e6376674a584b514853', '473271445a616f6e354d416c317a786e', '495a4d326a54715a3935486341543233', '5278796834484d623874697a446d6848', '374e6442524f44697148547364384273', '61536b6e7669425136696157564c7358', '615a346d6535484d7347646c37445479', '626a6465574e4376625548416f736e51', '4c685054656b77363171386d6f6e5168', '33773169734d364e6577694d7656534b', '384763394e346b756d466c7536737a5a', '41514b6e4f5136455671336471747470', '30427769696e36376e4f4d394170614d', '6b7469364f655565375636336d6a6c65', '31357a6279367a773639547357584e31', '483334313150554a61434b703547617a', '5676483866596735444739614c4b7577', '6c594a694b553151714c7952567a424b', '506f676765355762637a74317a31434e', '786147664430485a706a6d4a51503177', '464754396c6e7a6278534343766f7536', '486337486a446e4e57757047656d7169', '48776279484c786157495071504a7750', '71707a3772676836756f634175355a36', '506764317344463147684f6e4a393550', '5334477a3774416b4768525876496976', '74716755776a4e6a3477365a4a6c7332', '75506b68436779726f7059794d6e5267', '4e46516a3959496d644d49754f36694d', '6e696b673542414c414f51484953444e', '33416b7a796c52776867377649676150', '677862566f694342444f4a4d35744f43', '54354f577275434d3375325936756f54', '37794571546a38314370705567694a78']
res=[1, 7, 7, 9, 8, 3, 9, 13, 11, 13, 12, 13, 10, 11, 4, 4, 14, 12, 3, 12, 9, 14, 6, 20, 2, 13, 12, 10, 4, 9, 10, 12, 8, 10, 9, 21, 12, 13, 1, 20, 9, 7, 4, 4, 12, 3, 18, 6, 27, 5, 9, 21, 17, 4, 12, 23, 8, 2, 6, 5, 9, 5, 13, 15, 9, 10, 12]

msgs = [h(bytes.fromhex(x)) for x in msg]
a = [x*y for x,y in zip(res, msgs)]

target = 2**256 - 666
print(sum(a)%(2**256))
print(target)
print(sum(res))

conn=remote('104.196.21.25',5000)
q= conn.recvuntil(b'Solution? ')
print(q)

sol = input()
conn.sendline(sol.encode())

rs = []
ss = []

for i in tqdm(range(len(msg))):
    for j in range(res[i]):
        conn.sendline(b'sign')
        conn.sendline(bytes.fromhex(msg[i]))
        conn.recvuntil(b'Message:')
        q= conn.recvline()
        r,s = map(int, q.strip().split(b' '))
        rs.append(r)
        ss.append(s)

conn.sendline(b'sign')
conn.sendline(bytes.fromhex(msg[1]))
conn.recvuntil(b'Message:')
q = conn.recvline()
r,s = map(int, q.strip().split(b' '))
rs.append(r)
ss.append(s)

msg0 = h(bytes.fromhex(msg[0]))
msg1 = h(bytes.fromhex(msg[1]))

k = (msg0 - msg1)*inverse(ss[0]-ss[-1], order) % order
priv = (ss[0] - inverse(k, order)*msg0)*inverse(rs[0], order) % order
print(priv)

conn.sendline(b'sign')
conn.sendline(bytes.fromhex(msg[0]))
conn.recvuntil(b'Message:')
q = conn.recvline()

kk = inverse((ss[2] - priv*rs[2])*inverse(h(bytes.fromhex(msg[1])), order), order) 

conn.sendline(b'exchange')
conn.recvuntil(b'Sign or Exchange? ')
q=conn.recvline()

flag=AES.new(long_to_bytes(int((kk*priv*G).x())%(2**128), blocksize=16), AES.MODE_CBC, iv=long_to_bytes(int((kk*priv*G).x())>>128, blocksize=16)).decrypt(bytes.fromhex(q.strip().decode()))
print(flag)