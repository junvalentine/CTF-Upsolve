from tqdm import *
import hmac
import hashlib
from pwn import *
from Crypto.Util.number import long_to_bytes

def sign_message(id: int, key_client: bytes, key_server: bytes, message: str) -> bytes:
    key_combined = xor(key_client, key_server)
    full_message = f'{id}{message}'.encode()

    signature = hmac.new(key_combined, full_message, hashlib.sha256).digest()
    return signature

def sign(payload, key_client: bytes, message: str, f=0):
    if f == 0:
        payload.append(b'sign')
    else:
        payload.append(b'lul')
        return 
    payload.append(key_client.hex().encode())
    payload.append(message.encode())
    

def get_flag(r, key_server: bytes, index):

    signature = sign_message(index, b'\0'*16, key_server, 'gib flag pls')

    r.sendline(b'verify')
    r.sendline(b'gib flag pls')
    r.sendline(signature.hex().encode())

s=[i+1 for i in range(4096)]
s1=[]
s2=[0 for i in range(65537)]
for i in s:
    j=5000
    while j<65536:
        if str(j).startswith(str(i)):
            if s2[j] == 1:
                j+=1
                continue
            assert j<65536
            s2[j] = 1
            s1.append([j,i])
            break
        j+=1

a={}
key_server = b''
payload=[]

sign(payload, b'\x00'*16,'',1)

for i in tqdm(range(16)):
    for j in range(1,257):
        id=256*i+j
        s = sign(payload, b'\x00'*(16+i), str(s1[id-1][0])[len(str(id)):])
        a[str(s1[id-1][0])] = id

for i in tqdm(range(4097,65535)):
    try:
        id=a[str(i)]
        ind=id//256
        brute=id%256
        s=sign(payload,b'\x00'*(16+ind)+long_to_bytes(brute),'')
    except:
        s=sign(payload, b'\x00'*16,'',1)
        continue

while True:
    r = remote('chal.hkcert23.pwnable.hk', 28009)
    r.sendlineafter('🎬 '.encode(), b'\n'.join(payload))
    o=r.clean(1)

    if o!=b'':
        index=sorted(s1)
        o = [x.split(b'\xf0\x9f\x93\x9d ')[1].decode() for x in o.split(b'\n') if b'\xf0\x9f\x93\x9d' in x]
        out = o[4096:]
        key=[0 for i in range(16)]
        for i in range(len(out)):
            if out[i] == o[index[i][1]-1]:
                key[index[i][1]//256] = index[i][1]%256

        key=b''.join([long_to_bytes(i) for i in key])
        print('Found key = ',key)

        get_flag(r, key, 65535)
        r.interactive()
        break
    
#hkcert23{y0u_h4v3_t0_el1m1n4t3_am6igu17y_7o_m1tig4t3_4mb19ui7y_4t74ck5}
