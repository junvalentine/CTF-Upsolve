from fastecdsa.curve import Curve
from fastecdsa.point import Point
import random
from Crypto.Util.number import *
from tqdm import tqdm
from pwn import *
import requests
from Crypto.Cipher import AES
from tqdm import tqdm

def Babai_closest_vector(B, target):
    # Babai's Nearest Plane algorithm
    M = B.LLL()
    G = M.gram_schmidt()[_sage_const_0 ]
    small = target
    for _ in range(_sage_const_1 ):
        for i in reversed(range(M.nrows())):
            c = ((small * G[i]) / (G[i] * G[i])).round()
            small -= M[i] * c
    return target - small

p = 0xffffffffffffffffffffffffffffffff7fffffff
N = p.bit_length()//8
F = GF(p)
a = F(0xffffffffffffffffffffffffffffffff7ffffffc)
b = F(0x1c97befc54bd7a8b65acf89f81d4d4adc565fa45)
n = 0x0100000000000000000001f4c8f927aed3ca752257
E = EllipticCurve(F, (a, b))
G = E(0x4a96b5688ef573284664698968c38bb913cbfc82, 0x23a628553168947d59dcc912042351377ac5fb32)
E.set_order(n)

d = F(1)
while d.is_square():
    d += 1

nt = 0xfffffffffffffffffffe0b3706d8512b358adda9
ET = E.quadratic_twist(d)
ET.set_order(nt)
GT = ET.gens()[0]

secp160r1 = Curve(
    "secp160r1",  # (str): The name of the curve
    p,  # (long): The value of p in the curve equation.
    a,  # (long): The value of a in the curve equation.
    b,  # (long): The value of b in the curve equation.
    q,  # (long): The order of the base point of the curve.
    G[0],  # (long): The x coordinate of the base point of the curve.
    G[1]  # (long): The y coordinate of the base point of the curve.
)
G = Point(G[0], G[1], curve=secp160r1)

data=[]
for base in tqdm(range(0,161,4)):
    while True:
        i = random.randint(1, 2 ** base - 1)
        P = long_to_bytes((G * i).x)
        try:
            P.decode()
            print(arr)
            if i not in arr:
                arr.append(i)
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            # print(str(e))
            continue
print(data)

# recheck data, cuz of lift_x
data1=[]
for i in data:
    g=G*i
    l= E.lift_x(g.xy()[0],all=True)
    if l[0].xy()[1]>l[1].xy()[1]:
        t=l[1]
    else:
        t=l[0]
    if t*inverse(i,n) == G:
        data1.append(i)
    else:
        data1.append(-i)
data=data1

conn=remote('invention.challs.open.ecsc2024.it',int(38011))
data=[1330841055298174299762989631304916988641772184983, -1227102965607654059354140575268771058100172445559, -1077242579358873796198163939170483570551446819450, -114147, -643983, -2515474, -76232832, -162130937, -559553535, -955431672, 4086074334, 573500091, 31143966157, 64265647497, 31253360206, -43598782979, -409816445456, -5239003897325, 4120109551536, -499036554432, 2528306855847, 8397662095796, 14939373670697, -22438694485042, -474826542345, -92216865683162, 164908934904241, 559712079216914, -55564188109753, -680089224290348, 1341380263723435, 11794826525243223, 28701802971433914, 72469123886098322, -72852057707967028, -334423692787442992, -1054082138184802932, 452061040076300342, 986059149590694993, 1794949398310389647, -16987010285975718155, 15922314106523829923, -7022819788442473781, 123823646276828723049, -679061320181405436392, -1009017618357256743082, 10516091330461680119709, -27449477401653698730662, -4557255029215547359109004, 53461375724620467609086629, -949406482258669251279829027, 1633717266450601385753957871, 237488478187615376820921390774, -921775832607958258582871395338, -30740454744855102679261054746522, 265803892925603659541199583171606, -10004336577473537402118227178747590, 273445075146038639241845087918771878, -2960056903922693094902924453713592987, -51771476973383792353202418350858959915, 1173721393770493998351523999533885846876, -17266483283118698952030832496353928500710, 26857111530651321224924318249622613314975, -2949221358647332178986972868773963300995543, -64717467279789928132523355345631663638895778, -1318773755091914870830755563624291099846361373, 13315583857180716110151474508618975549935385755, 194353836325317355275513521354817170563904257783]

q=conn.recvlines(4)

k1=int(q[0].split(b'= ')[1])
conn.sendline(b'hanni')
q=conn.recvline()
token=q.split(b'with ')[-1].strip()
print(k1,token)

payload = token + token
for i in data:
    g=G*i
    payload+=long_to_bytes(int(g.xy()[0]),20)

conn.sendline(payload.hex())

q=conn.recvlines(2)
pwd=q[1].split(b'password \'')[-1].strip().decode()[:-1]
print(pwd)
block1=bytes.fromhex(pwd[:2*N])
block2=bytes.fromhex(pwd[2*N:4*N])
block3=bytes.fromhex(pwd[4*N:])
print(block1,block2,block3)

target = (bytes_to_long(block1)-bytes_to_long(token)) * k1
for _ in range(10):
    arr = random.sample(data, 30)
    size=len(arr)
    print(arr,size)

    scale=2**160
    mat=[]
    for i in range(size):
        mat.append([0]*i+[1]+[0]*(size-1-i)+[0]+[scale*arr[i]])

    mat.append([0]*(size+1)+[scale*n])
    mat.append([0]*size+[2**160]+[-scale*target])
    mat=matrix(ZZ,mat)
    
    targetvec=vector(ZZ,[2**8 for i in range(size)]+[scale]+[0])
    sol = Babai_closest_vector(mat,targetvec)

    if all([i >= 0 for i in sol[:-1]]):
        summ=sum([sol[i]*arr[i] for i in range(len(sol[:-2]))])
        print(sol,summ%p, target%p)
        payload=token + block2 + block3
        for j in range(len(sol[:-2])):
            g=G*arr[j]
            payload+=long_to_bytes(int(g.xy()[0]),20)*sol[j]
        payload=payload.hex()
        conn.sendline(b'hanni')
        conn.sendline(payload)
        conn.interactive()
        break




