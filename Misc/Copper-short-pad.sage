PRxy.<x,y> = PolynomialRing(Zmod(n))
PRx.<xn> = PolynomialRing(Zmod(n))
PRZZ.<xz,yz> = PolynomialRing(Zmod(n))

g1 = x**e - crypto[1]
g2 = (x + y)**e - crypto[2]
 
q1 = g1.change_ring(PRZZ)
q2 = g2.change_ring(PRZZ)
 
h = q2.resultant(q1)
# need to switch to univariate polynomial ring
# because .small_roots is implemented only for univariate
h = h.univariate_polynomial() # x is hopefully eliminated
h = h.change_ring(PRx).subs(y=xn)
h = h.monic()
 
roots = h.small_roots(X=2**32, beta=0.49999)
print(roots)

diff=roots[0]
x = PRx.gen() # otherwise write xn
g1 = x**e - crypto[1]
g2 = (x + diff)**e - crypto[2]
 
# gcd
while g2:
    g1, g2 = g2, g1 % g2
 
g = g1.monic()
assert g.degree() == 1, "Failed 2"
 
# g = xn - msg
msg = -g[0]
print(msg)