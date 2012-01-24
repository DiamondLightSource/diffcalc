Section 5.4: Two sample and either a detector or pseudo angle given
===================================================================

in the following psi can be obtained from alpha, beta or a_eq_b

solved in paper are:

x chi, phi, psi/alpha/beta --- zaxis mode (zaxis horizontal with chi=0 and vertical with chi=90?)

x chi, phi, qaz/nu/delta

x mu, eta, psi/alpha/beta 

x mu, eta, qaz/nu/delta

not solved but required are:

mu, nu, phi (for three circle on i10 and i06)

all possible are:

(phi, chi, eta, mu)

phi, chi *solved with qaz and psi*
phi, eta
phi, mu *required with qaz, for i06 and i10*
chi, eta
chi, mu
eta, mu *solved with qaz and psi*



Fancy modes to add:

eta_half_delta (bisecting if qaz=90)

mu_half_nu (bisecting if qaz=0)


paths:

1 det, 1 ref, 1 samp
====================
0. calc theta
1. *ref* --> alpha
2. *det*, theta --> delta, nu (and qaz, naz)
3. *samp* and theta, qaz, naz --> phi, chi, eta, mu


1 ref, 2 samp
=============
e.g. chi, phi, psi

0. calc theta
1. *ref* --> psi
2. *2 samp* and psi --> phi, chi, eta, mu and qaz
3. qaz, theta --> nu, delta

1 det, 2 samp
=============
e.g. chi, phi, qaz

0. calc theta
1. *det*, theta --> delta, nu, (and qaz, naz)
2. *2 samp* and qaz --> phi, chi, eta, mu (and psi)
