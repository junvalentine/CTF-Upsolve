conn=remote('chal.amt.rs',1415)
# conn=process(['python3','chall.py'])
conn.recvline()
# F=conn.recvlines(256)
# F=[bytes.fromhex(i.decode()) for i in F]
payload=b''
for i in range(256):
	payload+=b'1\n'
	payload+=(b'\x00'+bytes([i])+b'\x00'*14).hex().encode()+b'\n'

conn.send(payload)
q=conn.recvlines(4*256)
res=[]
pos=[0 for i in range(256)]
for i in q:
	if b'hex:' not in i:
		continue
	else:
		f=i.split(b'hex:')[1].strip().decode()
		res.append(f)
for i in range(256):
	if res[i][-1]=='f':
		r=int(res[i],16)%256
		pos[r^i]+=1
f00=pos.index(16)
print(f00)

payload=b''
for i in range(256):
	payload+=b'1\n'
	payload+=(b'\x00'+long_to_bytes(f00)+bytes([i])+b'\x00'*13).hex().encode()+b'\n'
conn.send(payload)
q=conn.recvlines(4*256)

res=[]
pos=[0 for i in range(256)]
for i in q:
	if b'hex:' not in i:
		continue
	else:
		f=i.split(b'hex:')[1].strip().decode()
		res.append(f)
for i in range(256):
	if res[i][-1]=='f':
		r=int(res[i],16)%256
		pos[r^i^f00]+=1

f01=pos.index(16)
f0=[f00,f01]
payload=b'1\n'+(b'\x00'+bytes([f0[0],f0[1]^f0[0]^15])+b'\x00'*13).hex().encode()+b'\n'
conn.send(payload)
q=conn.recvlines(4)[-1].split(b'hex:')[1].strip().decode()
for i in range(0,len(q),2):
	f0.append(int(q[i:i+2],16)^f0[-1])
f0=f0[:15]
# assert bytes(f0)==F[0]

f=[f0]+[[] for i in range(255)]
print(f)
for i in range(1,256):
	if i%16==15:
		print('Step',i)
		payl=[0]*16
		payl[1]=i^f0[0]
		payload=b'1\n'+bytes(payl).hex().encode()+b'\n'
		print(payload)
		conn.send(payload)
		q=conn.recvlines(4)[-1].split(b'hex:')[1].strip().decode()
		fl=f0[1:15]+[0]
		ff=[]
		for j in range(0,len(q)-2,2):
			ff.append(int(q[j:j+2],16)^fl[j//2])
		f[i]=ff
		# assert bytes(ff)==F[i] , i
		print(ff,q[30:])

for i in range(1,256):
	if i%16!=15:
		print('Step',i)
		payload=b''
		for j in range(256):
			payl=[0]*16
			payl[0]=i
			payl[(i+1)%16]=j
			payload+=b'1\n'+ bytes(payl).hex().encode()+b'\n'
		conn.send(payload)
		q=conn.recvlines(4*256)
		
		res=[]
		pos=[0 for j in range(256)]
		for j in q:
			if b'hex:' not in j:
				continue
			else:
				qq=j.split(b'hex:')[1].strip().decode()
				res.append(qq)
		for j in range(256):
			if res[j][-1]=='f':
				r=int(res[j],16)%256
				pos[r^j]+=1

		ff=[0]*16
		ff[i%16]=pos.index(16)
		print(ff[i%16])

		payload=b''
		payl=[0]*16
		payl[0]=i
		payl[(i+1)%16]=ff[i%16]^15
		payload+=b'1\n'+ bytes(payl).hex().encode()+b'\n'
		conn.send(payload)
		q=conn.recvlines(4)[-1].split(b'hex:')[1].strip().decode()

		ind=0
		for j in range(14):
			if j!=(i%16):
				ff[ind]=int(q[j*2:j*2+2],16)^f[15][j]
				ind+=1
			else:
				ind+=1
				ff[ind]=int(q[j*2:j*2+2],16)^f[15][j]
				ind+=1
			
		f[i]=ff[:15]
		# print(bytes(ff[:15]),F[i])
		# assert bytes(ff[:15])==F[i] , i
		print(ff[:15],q[30:])
conn.sendline(b'2')
q=conn.recvlines(4)[-1].split(b'> ')[1].strip().decode()

flagg=b''
for i in range(0,len(q),32):
	flag=bytes.fromhex(q[i:i+32])
	idx = 15
	cand=[flag]

	for i in range(256):
		cand1=[]
		for f1 in cand:
			alpha=b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}!@#$%^&*()-=;'+ b'\x00'
			if all([long_to_bytes(i) in alpha for i in f1]) :
				flagg+=f1
				print('hanniiii found the flag:',f1)
				break
			if f1[-1]%16!=15:
				L, R = f1[:-1], f1[-1:]
				L, R = xor(L, bytes(f[R[0]])), R
				ind=L[-1]%16
				flag1 = L[:ind] + R + L[ind:]
				cand1.append(flag1)
			else:
				L, R = f1[:-1], f1[-1:]
				ind=L[-1]%16
				flag1 = L[:ind] + R + L[ind:]
				L, R = xor(L, bytes(f[R[0]])), R
				ind=L[-1]%16
				flag2 = L[:ind] + R + L[ind:]
				cand1.append(flag1)
				cand1.append(flag2)
		cand=cand1

print('hanniiii say gud night to you with flag:',flagg)