def calculate_solution_from_basis(basis):
    solution = {}
    
    # Parse each polynomial in the basis
    for poly in basis:
        poly_str = str(poly).strip()
        
        # Handle simple cases like "a0" (means variable = 0)
        if (poly_str.startswith('a') or poly_str.startswith('b')) and poly_str[1:].isdigit():
            var_name = poly_str
            solution[var_name] = 0
            
        # Handle cases like "a2 + 1" (means variable = 1)
        elif poly_str.endswith(' + 1'):
            var_name = poly_str[:-4]  # Remove ' + 1'
            solution[var_name] = 1
    
    # Convert bits to 32-bit integers
    def bits_to_int(prefix, num_bits=32):
        result = 0
        for i in range(num_bits):
            bit_val = solution.get(f'{prefix}{i}', 0)
            result |= (bit_val << i)
        return result
    
    A = bits_to_int('a')
    B = bits_to_int('b')
    
    return A, B

WORD = 0xFFFFFFFF
rol = lambda x, r: ((x << r) | (x >> (32 - r))) & WORD
ror = lambda x, r: ((x >> r) | (x << (32 - r))) & WORD

_ROUNDS = 24
_DELTA = [0xC3EFE9DB, 0x44626B02, 0x79E27C8A, 0x78DF30EC]

def fault(round, index):
    conn.sendline(b'1')
    conn.sendline(b'00'*16)
    payload = str(round) + ' ' + str(index)
    conn.sendline(payload.encode())
    conn.recvuntil(b'>')
    return conn.recvline().strip().decode()

def normal():
    conn.sendline(b'0')
    conn.sendline(b'00'*16)
    conn.recvuntil(b'>')
    return conn.recvline().strip().decode()

def step1(fau_state):
    global nor_state
    
    eqs = []
    Cn = ror(nor_state[0], 9)
    Cns = [(Cn>>i) % 2 for i in range(32)]

    As = [f"a{i}" for i in range(32)]
    Bs = [f"b{i}" for i in range(32)]
    ab = As + Bs
    As = PolynomialRing(GF(2), ab).gens()[:32]
    Bs = PolynomialRing(GF(2), ab).gens()[32:]
    eqs.append(Cns[0] - As[0] - Bs[0])
    eqs.append(Cns[1] - As[1] - Bs[1] - As[0]*Bs[0])
    for i in range(2,32):
        eqs.append(Cns[i] - As[i] - Bs[i] - As[i-1]*Bs[i-1] - (As[i-1] + Bs[i-1]) * (As[i-1] + Bs[i-1] + Cns[i-1]))
    
    for i in range(5):
        delta_B = nor_state[3] ^ fau_state[i][3]
        delta_Bs = [(delta_B >> i) % 2 for i in range(32)]
        
        Cf = ror(fau_state[i][0], 9) 
        Cfs = [(Cf >> i) % 2 for i in range(32)]
        
        eqs.append(Cfs[0] - As[0] - Bs[0] - delta_Bs[0])
        eqs.append(Cfs[1] - As[1] - Bs[1] - delta_Bs[1] - As[0]*(Bs[0] + delta_Bs[0]))
        for i in range(2,32):
            eqs.append(Cfs[i] - As[i] - Bs[i] - delta_Bs[i] - As[i-1]*(Bs[i-1] + delta_Bs[i-1]) - (As[i-1] + Bs[i-1] + delta_Bs[i-1]) * (As[i-1] + Bs[i-1] + delta_Bs[i-1] + Cfs[i-1]))
    
    # eqs.append(As[31]-1)
    
    I = Ideal(eqs)  
    I = I.groebner_basis()
    mono = I[0].monomials()
    print(mono)
    Ass = []
    Bss = []
    rk23_0s = []
    if len(mono) >1 and mono[-1] != 1:
        I = Ideal(eqs+[mono[-1] - 1])  
        I = I.groebner_basis()
        
        if len(list(I))>1:
            print('step 1')
            print(list(I))
        
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_0s.append(nor_state[3] ^ calculate_solution_from_basis(I)[1])

        I = Ideal(eqs+[mono[-1]])  
        I = I.groebner_basis()
        
        if len(list(I))>1:
            print('step 1')
            print(list(I))
        
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_0s.append(nor_state[3] ^ calculate_solution_from_basis(I)[1])
    else:
        if len(list(I))>1:
            print('step 1')
            print(list(I))

        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_0s.append(nor_state[3] ^ calculate_solution_from_basis(I)[1])

    return Ass, Bss, rk23_0s

def step2(A1, B1, fau_state):
    global nor_state
    
    eqs = []
    Cn = rol(nor_state[1], 5)
    Cns = [(Cn>>i) % 2 for i in range(32)]

    As = [f"a{i}" for i in range(32)]
    Bs = [f"b{i}" for i in range(32)]
    ab = As + Bs
    As = PolynomialRing(GF(2), ab).gens()[:32]
    Bs = PolynomialRing(GF(2), ab).gens()[32:]
    
    eqs.append(Cns[0] - As[0] - Bs[0])
    eqs.append(Cns[1] - As[1] - Bs[1] - As[0]*Bs[0])
    
    for i in range(2,32):
        eqs.append(Cns[i] - As[i] - Bs[i] - As[i-1]*Bs[i-1] - (As[i-1] + Bs[i-1]) * (As[i-1] + Bs[i-1] + Cns[i-1]))
    
    for i in range(5):
        a = (ror(fau_state[i][0], 9) - B1) & WORD

        delta_B = A1 ^ a
        delta_Bs = [(delta_B >> i) % 2 for i in range(32)]
        
        Cf = rol(fau_state[i][1], 5) 
        Cfs = [(Cf >> i) % 2 for i in range(32)]
        
        eqs.append(Cfs[0] - As[0] - Bs[0] - delta_Bs[0])
        eqs.append(Cfs[1] - As[1] - Bs[1] - delta_Bs[1] - As[0]*(Bs[0] + delta_Bs[0]))
        for i in range(2,32):
            eqs.append(Cfs[i] - As[i] - Bs[i] - delta_Bs[i] - As[i-1]*(Bs[i-1] + delta_Bs[i-1]) - (As[i-1] + Bs[i-1] + delta_Bs[i-1]) * (As[i-1] + Bs[i-1] + delta_Bs[i-1] + Cfs[i-1]))
    
    
    I = Ideal(eqs)
    I = I.groebner_basis()
    mono = I[0].monomials()
    print(mono, '2')
    
    Ass = []
    Bss = []
    rk23_12s = []
    
    if len(mono) > 1 and mono[-1] != 1:
        I = Ideal(eqs+[mono[-1] - 1])  
        I = I.groebner_basis()
        
        if len(list(I))>1:
            print('step 2')
            print(list(I))
        
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_12s.append(A1 ^ calculate_solution_from_basis(I)[1])

        I = Ideal(eqs+[mono[-1]])  
        I = I.groebner_basis()
        
        if len(list(I))>1:
            print('step 2')
            print(list(I))
        
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_12s.append(A1 ^ calculate_solution_from_basis(I)[1])
    else:
        if len(list(I))>1:
            print('step 2')
            print(list(I))
            
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])
        rk23_12s.append(A1 ^ calculate_solution_from_basis(I)[1])
        # rk23_12 = A1 ^ B

    return Ass, Bss, rk23_12s

def step3(A2, B2, fau_state):
    global nor_state
    
    eqs = []
    Cn = rol(nor_state[2], 3)
    Cns = [(Cn>>i) % 2 for i in range(32)]

    As = [f"a{i}" for i in range(32)]
    Bs = [f"b{i}" for i in range(32)]
    ab = As + Bs
    As = PolynomialRing(GF(2), ab).gens()[:32]
    Bs = PolynomialRing(GF(2), ab).gens()[32:]
    
    eqs.append(Cns[0] - As[0] - Bs[0])
    eqs.append(Cns[1] - As[1] - Bs[1] - As[0]*Bs[0])
    
    for i in range(2,32):
        eqs.append(Cns[i] - As[i] - Bs[i] - As[i-1]*Bs[i-1] - (As[i-1] + Bs[i-1]) * (As[i-1] + Bs[i-1] + Cns[i-1]))
    
    for i in range(5):
        a = (rol(fau_state[i][1], 5) - B2) & WORD

        delta_B = A2 ^ a
        delta_Bs = [(delta_B >> i) % 2 for i in range(32)]
        
        Cf = rol(fau_state[i][2], 3) 
        Cfs = [(Cf >> i) % 2 for i in range(32)]
        
        eqs.append(Cfs[0] - As[0] - Bs[0] - delta_Bs[0])
        eqs.append(Cfs[1] - As[1] - Bs[1] - delta_Bs[1] - As[0]*(Bs[0] + delta_Bs[0]))
        for i in range(2,32):
            eqs.append(Cfs[i] - As[i] - Bs[i] - delta_Bs[i] - As[i-1]*(Bs[i-1] + delta_Bs[i-1]) - (As[i-1] + Bs[i-1] + delta_Bs[i-1]) * (As[i-1] + Bs[i-1] + delta_Bs[i-1] + Cfs[i-1]))
    
    
    I = Ideal(eqs)
    I = I.groebner_basis()
    mono = I[0].monomials()
    print(mono)
    Ass = []
    Bss = []
    rk23_34s = []
    if len(mono) >1 and mono[-1] != 1:
        I = Ideal(eqs+[mono[-1] - 1])  
        I = I.groebner_basis()
        
        if len(list(I))>1:
            print('step 3')
            print(list(I))
        
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_34s.append(A2 ^ calculate_solution_from_basis(I)[1])

        I = Ideal(eqs+[mono[-1]])  
        I = I.groebner_basis()
        
        if len(list(I))>1:
            print('step 3')
            print(list(I))
        
        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_34s.append(A2 ^ calculate_solution_from_basis(I)[1])
    else:
        if len(list(I))>1:
            print('step 3')
            print(list(I))

        Ass.append(calculate_solution_from_basis(I)[0])
        Bss.append(calculate_solution_from_basis(I)[1])

        rk23_34s.append(A2 ^ calculate_solution_from_basis(I)[1])
    
    return Ass, Bss, rk23_34s

def step4(A3, B3, fau_state, rk230):
    global nor_state
    
    eqs = []
    Cn = ror(nor_state[3], 9)
    Cns = [(Cn>>i) % 2 for i in range(32)]

    As = [f"a{i}" for i in range(32)]
    Bs = [f"b{i}" for i in range(32)]
    ab = As + Bs
    As = PolynomialRing(GF(2), ab).gens()[:32]
    Bs = PolynomialRing(GF(2), ab).gens()[32:]
    
    eqs.append(Cns[0] - As[0] - Bs[0])
    eqs.append(Cns[1] - As[1] - Bs[1] - As[0]*Bs[0])
    
    for i in range(2,32):
        eqs.append(Cns[i] - As[i] - Bs[i] - As[i-1]*Bs[i-1] - (As[i-1] + Bs[i-1]) * (As[i-1] + Bs[i-1] + Cns[i-1]))
    
    for i in range(5):
        a = (rol(fau_state[i][2], 3) - B3) & WORD

        delta_B = A3 ^ a
        delta_Bs = [(delta_B >> i) % 2 for i in range(32)]
        
        Cf = ror(fau_state[i][3],9)
        Cfs = [(Cf >> i) % 2 for i in range(32)]
        
        eqs.append(Cfs[0] - As[0] - Bs[0] - delta_Bs[0])
        eqs.append(Cfs[1] - As[1] - Bs[1] - delta_Bs[1] - As[0]*(Bs[0] + delta_Bs[0]))
        for i in range(2,32):
            eqs.append(Cfs[i] - As[i] - Bs[i] - delta_Bs[i] - As[i-1]*(Bs[i-1] + delta_Bs[i-1]) - (As[i-1] + Bs[i-1] + delta_Bs[i-1]) * (As[i-1] + Bs[i-1] + delta_Bs[i-1] + Cfs[i-1]))
    
    
    I = Ideal(eqs)
    I = I.groebner_basis()
    if len(list(I))>1:
        print('step 4')
        print(list(I))
    
    A, B = calculate_solution_from_basis(I)
    
    rk22_0 = (ror(rk230, 1) - rol(_DELTA[3],23)) % WORD
    
    x22_0 = B ^ rk22_0
    
    rk23_5 = x22_0 ^ A3
    return A, B, rk23_5
def rev_key(last_rk):
    T = [last_rk[0], last_rk[1], last_rk[2], last_rk[4]]  # T[0], T[1], T[2], T[3]
    
    # Work backwards through all rounds
    for i in range(24 - 1, -1, -1):
        # Calculate the delta values for this round (same as forward)
        t0 = rol(_DELTA[i & 3], i & 31)
        t1 = rol(_DELTA[i & 3], (i + 1) & 31)
        t2 = rol(_DELTA[i & 3], (i + 2) & 31)
        t3 = rol(_DELTA[i & 3], (i + 3) & 31)
        
        T[0] = (ror(T[0], 1) - t0) & WORD
        T[1] = (ror(T[1], 3) - t1) & WORD
        T[2] = (ror(T[2], 6) - t2) & WORD
        T[3] = (ror(T[3], 11) - t3) & WORD
    
    key = b''
    for i in range(4):
        key += T[i].to_bytes(4, 'little')
    
    return key

conn=process(['python3.12', '/mnt/d/ctf/chall.py'])
conn=remote('43.201.153.112',10955)

q = conn.recvuntil("python3 <(curl -sSL https://goo.gle/kctf-pow) solve ")
prob = conn.recvline()[:-1].decode()
os.system(f"python3 pow.py solve {prob} > res")
conn.sendlineafter("Solution? ", open("res", 'r').read())
# conn.interactive()
# key = eval(conn.recvline())
nor_ct = bytes.fromhex(normal())
nor_state = [int.from_bytes(nor_ct[i * 4 : (i + 1) * 4], "little") for i in range(4)]

fau_state1 =[]
for i in range(5):
    fau_ct = bytes.fromhex(fault(22, 0))
    fau_state1.append([int.from_bytes(fau_ct[i * 4 : (i + 1) * 4], "little") for i in range(4)])
fau_state2 =[]
for i in range(5):
    fau_ct = bytes.fromhex(fault(23, 1))
    fau_state2.append([int.from_bytes(fau_ct[i * 4 : (i + 1) * 4], "little") for i in range(4)])
fau_state3 =[]
for i in range(5):
    fau_ct = bytes.fromhex(fault(23, 2))
    fau_state3.append([int.from_bytes(fau_ct[i * 4 : (i + 1) * 4], "little") for i in range(4)])
    
A1s, B1s, rk23_0s = step1(fau_state1)

# print(bin((key[1]^key[2]) % (2**31)))
# print(bin((key[3]^key[4]) % (2**31)))
# print(bin(key[5] % (2**31)))

for i1 in range(len(A1s)):
    A1 = A1s[i1] % (2**31)
    B1 = B1s[i1] % (2**31)
    rk23_0 = rk23_0s[i1] % (2**31)
    # print(bin(rk23_0), 1)
    # print(bin(key[0]%2**31))
    for i2 in range(4):
        A2s, B2s, rk23_12s = step2(2**31*((i2>>1)%2) + A1, 2**31*(i2%2) + B1, fau_state2)
        
        rk230 = (2**31*(i2%2) + B1) ^ nor_state[3]
        
        for i22 in range(len(A2s)):
            A2 = A2s[i22] % (2**31)
            B2 = B2s[i22] % (2**31)
            rk23_12 = rk23_12s[i22] % (2**31)
            # print(bin(rk23_12), 2)
            # print(bin((key[1]^key[2]) % (2**31)))
            
            for i3 in range(4):
                A3s, B3s, rk23_34s = step3(2**31*((i3>>1)%2) + A2, 2**31*(i3%2) + B2, fau_state3)
                
                rk2312 = (2**31*(i3%2) + B2) ^ (2**31*((i2>>1)%2) + A1)
                
                for i33 in range(len(A3s)):
                    A3 = A3s[i33] % (2**31)
                    B3 = B3s[i33] % (2**31)
                    rk23_34 = rk23_34s[i33] % (2**31)
                    # print(bin(rk23_34), 3)
                    # print(bin((key[3]^key[4]) % (2**31)))
                    
                    for i4 in range(4):
                        A4, B4, rk23_5 = step4(2**31*((i4>>1)%2) + A3, 2**31*(i4%2) + B3, fau_state1, rk230)
                        
                        rk2334 = (2**31*(i4%2) + B3) ^ (2**31*((i3>>1)%2) + A2)

                        A4 = A4 % (2**31)
                        B4 = B4 % (2**31)
                        rk23_5 = rk23_5 % (2**31)
                        
                        # if rk23_5 == key[5] % (2**31):
                        #     print(bin(rk23_5))
                        #     print(bin(key[5] % (2**31)))
                        
                        for j in range(2):
                            if j == 0:
                                rk235= rk23_5
                                rk23 = [rk230, rk235, rk2312 ^ rk235, rk235, rk2334 ^ rk235, rk235]
                                keyy = rev_key(rk23)
                            if j == 1:
                                rk235 = rk23_5 + 2**31
                                rk23 = [rk230, rk235, rk2312 ^ rk235, rk235, rk2334 ^ rk235, rk235]
                                keyy = rev_key(rk23)
                            # if rk23_5 == key[5] % (2**31):
                            #     print('key', keyy.hex(),long_to_bytes(key[6]).hex())
                            import chall1 
                            if chall1.encrypt(bytes.fromhex('00'*16), keyy) == nor_ct:
                                print("Key found:", keyy.hex())
                                conn.sendline(keyy.hex().encode())
                                conn.interactive()