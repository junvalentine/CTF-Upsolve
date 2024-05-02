import random
from hashlib import sha512 
from Crypto.Util.number import *
from pwn import *
from copy import deepcopy, copy

class Random:
    def __init__(self, seed):
        self.seed = seed
        # print(seed)
        if seed < 0:
            self.init_key = self.split_seed(-seed)
        else:
            self.init_key = self.split_seed(seed)
        self.init_by_array()

    def split_seed(self,seed):
        seed_chunks = []
        while seed > 0:
            seed_chunks.append(seed & 0xffffffff)
            seed >>= 32
        return seed_chunks
        
    def init_genrand(self, s):
        N = 624  # The size of the state vector in the Mersenne Twister algorithm
        self.state = [0] * N
        self.state[0] = s
        for mti in range(1, N):
            self.state[mti] = (1812433253 * (self.state[mti-1] ^ (self.state[mti-1] >> 30)) + mti) & 0xffffffff
        self.index = N
    def fake_init_genrand(self, s):
        N = 624  # The size of the state vector in the Mersenne Twister algorithm
        state = [0] * N
        state[0] = s
        for mti in range(1, N):
            state[mti] = (1812433253 * (state[mti-1] ^ (state[mti-1] >> 30)) + mti) & 0xffffffff
        return state
    def init_by_array(self):
        N = 624  # The size of the state vector in the Mersenne Twister algorithm
        self.init_genrand(19650218)
        i = 1
        j = 0
        k = max(N, len(self.init_key))
        # print(len(init_key))
        # print(self.state)
        for _ in range(k):
            # print(i)
            # print(j)
            self.state[i] = ((self.state[i] ^ ((self.state[i-1] ^ (self.state[i-1] >> 30)) * 1664525)) + self.init_key[j] + j) & 0xffffffff
            i += 1
            j += 1
            if i >= N:
                self.state[0] = self.state[N-1]
                i = 1
            if j >= len(self.init_key):
                j = 0
        print('state12')
        print(self.state)
        for _ in range(N - 1):
            # print(i)
            self.state[i] = ((self.state[i] ^ ((self.state[i-1] ^ (self.state[i-1] >> 30)) * 1566083941)) - i) & 0xffffffff # mod 2**32
            i += 1
            if i >= N:
                self.state[0] = self.state[N-1]
                i = 1
        self.state[0] = 0x80000000  # MSB is 1; assuring non-zero initial array
    def getstate(self):
        return self.state
    def solve_key(self,length,init):
        # length must be divided by 624 
        N = 624
        state=deepcopy(self.state)
        for i in range(N,1,-1):
            if i == N:
                state[0] = state[N-1]
                state[1] = ((state[1] + 1) ^ ((state[0]^(state[0]>>30)) * 1566083941)) & 0xffffffff
            else:
                state[i]= ((state[i] + i)  ^ ((state[i-1]^(state[i-1]>>30)) * 1566083941)) & 0xffffffff
        state[0] = state[N-1]
        
        state1=self.fake_init_genrand(19650218)
        key=[0]*length
        key[0]=init
        state1[1]=((state1[1] ^ ((state1[0] ^ (state1[0] >> 30)) * 1664525)) + key[0] + 0) & 0xffffffff
        for i in range(2,N+1):
            j = (i - 1) % length
            if i == N:
                state1[0] = state1[N-1]
                key[j]= (state[1]- j - (state1[1] ^ ((state1[0] ^ (state1[0] >> 30)) * 1664525))) % 2**32
            else:
                key[j] = (state[i]- j - (state1[i] ^ ((state1[i-1] ^ (state1[i-1] >> 30)) * 1664525))) % 2**32
                state1[i]=state[i]
        # for i in range(N,0,-1):
        #     j = (i-1) % len(self.init_key)
        #     if i == N:
        #         state[0] = state[N-1]
        #         state[1] = ((state[1] - j - self.init_key[j]) ^ ((state[0]^(state[0]>>30)) * 1664525)) & 0xffffffff
        #     else:
        #         state[0] = 19650218
        #         state[i] = ((state[i] - j - self.init_key[j]) ^ ((state[i-1]^(state[i-1]>>30)) * 1664525)) & 0xffffffff
        key=sum([key[i]*2**(32*i) for i in range(len(key))])
        return key
    def solve_key1(self,length,key_init):
        N = 624
        state=copy(self.state)
        for i in range(N,1,-1):
            if i == N:
                state[0] = state[N-1]
                state[1] = ((state[1] + 1) ^ ((state[0]^(state[0]>>30)) * 1566083941)) & 0xffffffff
            else:
                state[i]= ((state[i] + i)  ^ ((state[i-1] ^ (state[i-1]>>30)) * 1566083941)) & 0xffffffff
        state[0] = state[N-1]
        # print(state)

        state1=self.fake_init_genrand(19650218)

        key=[]
        while key_init > 0:
            key.append(key_init & 0xffffffff)
            key_init >>= 32
        key+=[0]*(length-len(key))

        i=1
        j=0
        for _ in range(623*(length//623-1)+1):
            state1[i]=((state1[i] ^ ((state1[i-1] ^ (state1[i-1] >> 30)) * 1664525)) + key[j] + j) & 0xffffffff
            i += 1
            j += 1
            if i >= N:
                state1[0] = state1[N-1]
                i = 1
            if j >= len(key):
                j = 0

        for _ in range(N-1):
            key[j] = (state[i]- j - (state1[i] ^ ((state1[i-1] ^ (state1[i-1] >> 30)) * 1664525))) & 0xffffffff
            state1[i]=((state1[i] ^ ((state1[i-1] ^ (state1[i-1] >> 30)) * 1664525)) + key[j] + j) & 0xffffffff
            i += 1
            j += 1
            if i >= N:
                state1[0] = state1[N-1]
                i = 1
            if j >= len(key):
                j = 0
        key=sum([key[i]*2**(32*i) for i in range(len(key))])
        return state1,key

# ---------------------------------------------------------------------TESTING----------------------------------------------------------------------
# strr="Merry Christmas! You are the True winner, regardless of the ranking, running nonstop towards your dreams! Thanks for playing, and have fun!!"

# s4 = bytes_to_long(strr.encode() + sha512(strr.encode()).digest())
# s5 = -s4

# seed=s4
# a=Random(seed)
# print('final state')

# key_init=bytes_to_long(strr.encode())
# k=a.solve_key1(623*3+1,key_init)
# print(k[0],1)
# print(k[1])

# assert a.getstate()+[624]==list(random.Random(seed).getstate()[1])

strr="Merry Christmas! You are the True winner, regardless of the ranking, running nonstop towards your dreams! Thanks for playing, and have fun!!"
key_init=bytes_to_long(strr.encode())
s4 = bytes_to_long(strr.encode() + sha512(strr.encode()).digest())
s5 = -s4
a=Random(s4)
s3=a.solve_key(624,0)
s2=a.solve_key1(623*2+1,key_init)[1]
s1=a.solve_key1(623*3+1,key_init)[1]

assert 0 <= s4 < 2**2000
assert 2**2000 <= s3 < 2**20000
assert 2**20000 <= s2 < 2**40000
assert 2**40000 <= s1 < 2**80000
assert strr == s1.to_bytes(10000, "big")[-len(strr):].decode() 
assert random.Random(s1).getstate()[1]==random.Random(s4).getstate()[1]==random.Random(s5).getstate()[1]==random.Random(strr).getstate()[1]==random.Random(strr.encode()).getstate()[1]==random.Random(s3).getstate()[1]==random.Random(s2).getstate()[1]

conn=remote('host3.dreamhack.games',12559,level='debug')
payload=str(s1).encode()+b'\n'+str(s2).encode()+b'\n'+str(s3).encode()+b'\n'+str(s4).encode()+b'\n'+str(s5).encode()+b'\n'+strr.encode()+b'\n'+(strr.encode().hex()).encode()+b'\n'
conn.sendline(payload)
conn.recvlines(10)