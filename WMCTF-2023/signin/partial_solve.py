import gmpy2
from Crypto.Util.number import *
import itertools
from tqdm import *
from pwn import *
from Crypto.Cipher import *
from Crypto.Hash import *
from hashlib import *
from Crypto.Util.Padding import *
from Crypto.Util.number import *

a=0x7cda79f57f60a9b65478052f383ad7dadb714b4f4ac069997c7ff23d34d075fca08fdf20f95fbc5f0a981d65c3a3ee7ff74d769da52e948d6b0270dd736ef61fa99a54f80fb22091b055885dc22b9f17562778dfb2aeac87f51de339f71731d207c0af3244d35129feba028a48402247f4ba1d2b6d0755baff6
print(a)
conn=remote('1.13.101.243',27573)
q=conn.recvlines(26)

N=int(q[-2].decode())
gift=int(q[-1].decode())
bs=[]
rs=[]
for i in range(1<<16):
    cand=[(0,i)]
    cur=1
    while cur<=512:
        nxt_cand=[]
        for p_bit in [0,1]:
            for pp,qq in cand:
                nxtp=pp+p_bit*(1<<(cur-1))
                nxtq=qq
                if nxtp*nxtq % (1<<cur) == N % (1<<cur):
                    nxtq+= ((gift^nxtp)&(1<<(cur-1)))*(1<<16)
                    nxt_cand.append((nxtp,nxtq))
        cur+=1
        cand=nxt_cand
        if len(cand)==0:
            break
    if len(cand)==1:
        if N%int(cand[0][0])==0:
            print('hanni yay')
            print(int(cand[0][0]))
            conn.sendline(str(cand[0][0]))
            q=conn.recvlines(2)
            bs=q[0].strip(b'[]').split(b',')
            rs=q[1].strip(b'[]').split(b',')
