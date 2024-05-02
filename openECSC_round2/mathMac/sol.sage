from sage.all import *
from Crypto.Util.number import *
from pwn import *
from tqdm import tqdm
import random

p=8636821143825786083
Zp = GF(p)

while True:
    print('hanni')
    conn=remote('mathmac.challs.open.ecsc2024.it',38013)
    conn.recvline()

    hist=[]
    queries=66
    conn.send(b'1\n'*queries)
    for i in tqdm(range(queries)):
        q=conn.recvlines(4)
        out=q[-1].split(b'> ')[-1].split(b',')
        x=int(out[0])
        tag=int(out[1])
        hist.append((x,tag))

    mat=[]
    ress=[]
    for i in range(queries):
        x,tag=hist[i]
        row=ZZ(x).digits(2)
        while len(row)<64:
            row.append(0)
        row.append(1)
        mat.append(row)
        ress.append(int(Zp(tag).log(Zp(4))))

    mat=matrix(ZZ,mat)
    mat=mat.augment(identity_matrix(queries))

    res=mat.echelon_form()[0]
    res1=mat.echelon_form()[-2]
    print(res)
    print(res1)

    if res[0]==1 and res1[64]==1:
        res=res+res1
        print(res)

        sol=1
        for i in range(len(res[65:])):
            if res[65+i]>=0:
                sol*=int(pow(ress[i],res[65+i],(p-1)//2))
            else:
                sol*=inverse(int(pow(ress[i],-res[65+i],(p-1)//2)),(p-1)//2)
            sol%=(p-1)//2

        conn.sendline(b'2')
        conn.sendline(b'1,'+str(pow(2,2*int(sol),p)).encode())
        conn.interactive()
    else:
        conn.close()
        continue