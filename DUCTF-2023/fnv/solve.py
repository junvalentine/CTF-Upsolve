from sage.all import *

def Babai_closest_vector(M, G, target):
    small = target
    for _ in range(1):
        for i in reversed(range(M.nrows())):
            c = ((small * G[i]) / (G[i] * G[i])).round()
            small -= M[i] * c
    return target - small

h =    14695981039346656037
a =    1099511628211
b =    18446744073709551615+1
target=1384596537706222391

mat=[]
deg=10
for i in range(1,deg):
    mat.append([pow(a,i,b)]+[0]*(i-1)+[1]+[0]*(deg-i-1))
mat.append([b]+[0]*(deg-1))

mat=Matrix(ZZ,mat)
targett=vector(ZZ,[(target-h*pow(a,deg,b))%b]+[0]*(deg-1))

mat=mat.LLL()
G=mat.gram_schmidt()[0]
cvp=Babai_closest_vector(mat,G,targett)
print((target-h*pow(a,deg,b))%b)
print(cvp)

s=[]
h1=h
for i in reversed(range(1,len(cvp))):
    h1*=a
    h1%=b
    s.append(h1^(h1+cvp[i]))
    h1+=cvp[i]

s.append((target-h*pow(a,deg,b))%b-cvp[0])
# solution
print(bytes(s).hex())
# check
h1=h
for i in s:
    h1 *= 0x00000100000001b3
    h1 &= (b-1)
    h1 ^= i
print(h1)