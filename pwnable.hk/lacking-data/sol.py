def int_sha256(value: int) -> int:
    return int.from_bytes(hashlib.sha256(value.to_bytes(32, "little")).digest(), "little")

conn=remote('c06-lacking-data.kaze.chal.sh',1337,ssl=True)
ct = bytes.fromhex(conn.recvline().split(b'(hex): ')[1].strip().decode())
print(ct)

res=[]
us=[]
for i in range(4):
    conn.sendline(b'0 1 2 3 4')
    q= conn.recvline().split(b': ')[1].strip().split(b' ')
    us.append([int(x) for x in q])

mat=[]
for i in range(3):
    row=[us[i][0],us[i][1], 1]
    mat.append(row)
det= Matrix(mat).det()

mat=[]
for i in range(3):
    row=[us[i+1][0],us[i+1][1], 1]
    mat.append(row)
det1 = Matrix(mat).det()

p = list(factor(int(gcd(det,det1))))[-1][0]

x1,x2 = PolynomialRing(Zmod(p),['x1','x2']).gens()
I = ideal([3*x1*us[i][0] + x2*us[i][1] - 1 for i in range(4)])
x1=-I.groebner_basis()[0].coefficients()[1]%p
x2=-I.groebner_basis()[1].coefficients()[1]%p
print(x1,x2)

conn.sendline(b'0 1 2 3 5')
q= conn.recvline().split(b': ')[1].strip().split(b' ')
us.append([int(x) for x in q])

x = PolynomialRing(Zmod(p), 'x').gen()
I1 = ideal(3*x1*us[-1][0]*(x+int_sha256(5)) + x2*us[-1][1]*(x+int_sha256(5)) - (x+int_sha256(4)))
a=-I1.groebner_basis()[0].coefficients()[0]%p
print(a)

f = prod(a + int_sha256(i) for i in [0,1,2,3,4])
k1 = x2*inverse(f, p) % p
k2 = x1*inverse(f, p) % p

secret_key = (p, a, k1, k2)
derived_key = hashlib.sha256(str(secret_key).encode()).digest()[:16]
cipher = AES.new(derived_key, AES.MODE_CBC, iv = ct[:16 ])

print(cipher.decrypt(ct[16:]))