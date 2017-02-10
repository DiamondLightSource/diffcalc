# Diffcalc - A Diffraction Condition Calculator for Diffractometer Control

Diffcalc is a diffraction condition calculator used for controlling diffractometers within reciprocal lattice space. It performs the same task as the fourc, sixc, twoc, kappa, psic and surf macros from SPEC.

Diffcalc’s standard calculation engine is an implementation of [You1999] . The first versions of Diffcalc were based on [Vlieg1993] and [Vlieg1998] and a ‘Vlieg’ engine is still available. The ‘You’ engine is more generic and the plan is to remove the old ‘Vlieg’ engine once beamlines have been migrated. New users should use the ‘You’ engine. [*]

The foundations for this type of calculation were laid by by Busing & Levi in their classic paper [Busing1967]. Diffcalc’s orientation algorithm is taken from this paper. Busing & Levi also provided the original definition of the coordinate frames and of the U and B matrices used to describe a crystal’s orientation and to convert between Cartesian and reciprical lattice space.

Geometry plugins are used to adapt the six circle model used internally by Diffcalc to apply to other diffractometers. These contain a dictionary of the ‘missing’ angles which Diffcalc uses to constrain these angles internally, and a methods to map from external angles to Diffcalc angles and visa versa.

## Trying it out
### Check your environment
Change directory to the diffcalc project (python adds the current
working directory to the path):

```bash
$ cd diffcalc
$ ls
COPYING  diffcalc  doc  example  mock.py  mock.pyc  model  numjy  test
```
If using Python or iPython make sure numpy and diffcalc can be imported::

```bash
$ python 
Python 2.7.2+ (default, Oct  4 2011, 20:06:09) 
[GCC 4.6.1] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import numpy
>>> import diffcalc
```
If using Jython make sure Jama and diffcalc can be imported::

```bash
$ jython -Dpython.path=<diffcalc_root>:<path_to_Jama>/Jama-1.0.1.jar

Jython 2.2.1 on java1.5.0_11
Type "copyright", "credits" or "license" for more information.
>>> import Jama
>>> import diffcalc
```
### Run a dummy six circle configuration

With Python start the sixcircle.py example startup script (notice the -i and -m) and type demo_all():
```
$ python -i -m example/sixcircle
>>> demo_all()
...
```
Or with IPython, which will process input in a way similar to Diamond's OpenGDA project:
```
$ ipython -i example/sixcircle.py
>>> demo_all()
demo_all()
ORIENT


>>> help ub

STATE

   newub {'name'}                  start a new ub calculation name
   loadub {'name'|num}             load an existing ub calculation
   listub                          list the ub calculations available to load.
   saveubas 'name'                 save the ub calculation with a new name

LATTICE

   setlat                          interactively enter lattice parameters
                                   (Angstroms and Deg)
   setlat name a                   assumes cubic
   setlat name a b                 assumes tetragonal
   setlat name a b c               assumes ortho
   setlat name a b c gamma         assumes mon/hex with gam not equal to 90
   setlat name a b c alpha beta gamma 
                                   arbitrary
   c2th [h k l]                    calculate two-theta angle for reflection

SURFACE

   sigtau {sigma tau}              sets or displays sigma and tau

REFLECTIONS

   showref                         shows full reflection list
   addref                          add reflection interactively
   addref [h k l] {'tag'}          add reflection with current position and
                                   energy
   addref [h k l] (p1,p2...pN) energy {'tag'} 
                                   add arbitrary reflection
   editref num                     interactively edit a reflection.
   delref num                      deletes a reflection (numbered from 1)
   swapref                         swaps first two reflections used for
                                   calulating U matrix
   swapref num1 num2               swaps two reflections (numbered from 1)

UB

   checkub                         show calculated and entered hkl values for
                                   reflections.
   setu {((,,),(,,),(,,))}         manually set u matrix
   setub {((,,),(,,),(,,))}        manually set ub matrix
   calcub                          (re)calculate u matrix from ref1 and ref2.
   trialub                         (re)calculate u matrix from ref1 only (check
                                   carefully).

>>> pos wl 1
wl:       1.0000

>>> newub 'test'

>>> setlat 'cubic' 1 1 1 90 90 90

>>> ub
UBCALC

   name:          test
   sigma:      0.00000
   tau:        0.00000

CRYSTAL

   name:         cubic

   a, b, c:    1.00000   1.00000   1.00000
              90.00000  90.00000  90.00000

   B matrix:   6.28319   0.00000   0.00000
               0.00000   6.28319  -0.00000
               0.00000   0.00000   6.28319

UB MATRIX

   <<< none calculated >>>

REFLECTIONS

   <<< none specified >>>

>>> c2th [1 0 0]

>>> pos sixc [0 60 0 30 0 0]
sixc:     mu: 0.0000 delta: 60.0000 gam: 0.0000 eta: 30.0000 chi: 0.0000 phi: 0.0000 

>>> addref [1 0 0]

>>> c2th [0 1 0]

>>> pos phi 90
phi:      90.0000

>>> addref [0 1 0]
Calculating UB matrix.

>>> ub
UBCALC

   name:          test
   sigma:      0.00000
   tau:        0.00000

CRYSTAL

   name:         cubic

   a, b, c:    1.00000   1.00000   1.00000
              90.00000  90.00000  90.00000

   B matrix:   6.28319   0.00000   0.00000
               0.00000   6.28319  -0.00000
               0.00000   0.00000   6.28319

UB MATRIX

   U matrix:   1.00000   0.00000   0.00000
              -0.00000   1.00000   0.00000
               0.00000   0.00000   1.00000

   UB matrix:  6.28319   0.00000   0.00000
              -0.00000   6.28319  -0.00000
               0.00000   0.00000   6.28319

REFLECTIONS

     ENERGY     H     K     L        MU    DELTA      GAM      ETA      CHI      PHI  TAG
   1 12.398  1.00  0.00  0.00    0.0000  60.0000   0.0000  30.0000   0.0000   0.0000  
   2 12.398  0.00  1.00  0.00    0.0000  60.0000   0.0000  30.0000   0.0000  90.0000  

>>> checkub

     ENERGY     H     K     L    H_COMP   K_COMP   L_COMP     TAG
 1  12.3984  1.00  0.00  0.00    1.0000   0.0000   0.0000        
 2  12.3984  0.00  1.00  0.00   -0.0000   1.0000   0.0000        

CONSTRAIN


>>> help hkl

CONSTRAINTS

   con                             list available constraints and values
   con <name> {val}                constrains and optionally sets one constraint
   con <name> {val} <name> {val} <name> {val} 
                                   clears and then fully constrains
   uncon <name>                    remove constraint

HKL

   allhkl [h k l]                  print all hkl solutions ignoring limits

HARDWARE

   hardware                        show diffcalc limits and cuts
   setcut {axis_scannable {val}}   sets cut angle
   setcut {name {val}}             sets cut angle
   setmin {axis {val}}             set lower limits used by auto sector code
                                   (None to clear)
   setmax {name {val}}             sets upper limits used by auto sector code
                                   (None to clear)

MOTION

   sim hkl scn                     simulates moving scannable (not all)
   _sixc                           show Eularian position
   pos _sixc [mu, delta, gam, eta, chi, phi]  
                                   move to Eularian position(None holds an axis
                                   still)
   sim _sixc [mu, delta, gam, eta, chi, phi] 
                                   simulate move to Eulerian position_sixc
   hkl                             show hkl position
   pos hkl [h k l]                 move to hkl position
   pos {h|k|l} val                 move h, k or l to val
   sim hkl [h k l]                 simulate move to hkl position

>>> con qaz 90
!   2 more constraints required
    qaz: 90.0000

>>> con a_eq_b
!   1 more constraint required
    qaz: 90.0000
    a_eq_b

>>> con mu 0
    qaz: 90.0000
    a_eq_b
    mu: 0.0000

>>> con
    DET        REF        SAMP
    ======     ======     ======
    delta  --> a_eq_b --> mu
    gam        alpha      eta
--> qaz        beta       chi
    naz        psi        phi
                          mu_is_gam

    qaz: 90.0000
    a_eq_b
    mu: 0.0000

    Type 'help con' for instructions

>>> setmin delta 0

>>> setmin chi 0
SCAN


>>> pos hkl [1 0 0]
hkl:      h: 1.00000 k: 0.00000 l: 0.00000 

>>> scan delta 40 80 10 hkl ct 1
  delta        h        k        l       ct
-------  -------  -------  -------  -------
40.0000  0.67365  0.11878  0.00000  0.00959
50.0000  0.84202  0.07367  0.00000  0.87321
60.0000  1.00000  0.00000  0.00000  3.98942
70.0000  1.14279  -0.09998  0.00000  0.87321
80.0000  1.26604  -0.22324  0.00000  0.00959

>>> pos hkl [0 1 0]
hkl:      h: -0.00000 k: 1.00000 l: 0.00000 

>>> scan h 0 1 .2 k l sixc ct 1
       h        k        l      mu    delta     gam      eta     chi      phi       ct
--------  -------  -------  ------  -------  ------  -------  ------  -------  -------
-0.00000  1.00000  0.00000  0.0000  60.0000  0.0000  30.0000  0.0000  90.0000  3.98942
 0.20000  1.00000  0.00000  0.0000  61.3146  0.0000  30.6573  0.0000  78.6901  0.53991
 0.40000  1.00000  0.00000  0.0000  65.1654  0.0000  32.5827  0.0000  68.1986  0.00134
 0.60000  1.00000  0.00000  0.0000  71.3371  0.0000  35.6685  0.0000  59.0362  0.00134
 0.80000  1.00000  0.00000  0.0000  79.6302  0.0000  39.8151  0.0000  51.3402  0.53991
 1.00000  1.00000  0.00000  0.0000  90.0000  0.0000  45.0000  0.0000  45.0000  3.98942

>>> con psi
    qaz: 90.0000
!   psi: ---
    mu: 0.0000

>>> scan psi 0 90 10 hkl [1 0 1] eta chi phi ct .1
    psi     eta      chi      phi        h        k        l       ct
-------  ------  -------  -------  -------  -------  -------  -------
0.00000  0.0000  90.0000  90.0000  1.00000  0.00000  1.00000  0.39894
10.00000  0.4385  82.9470  82.8929  1.00000  -0.00000  1.00000  0.39894
20.00000  1.7808  76.0046  75.5672  1.00000  -0.00000  1.00000  0.39894
30.00000  4.1066  69.2952  67.7923  1.00000  -0.00000  1.00000  0.39894
40.00000  7.5463  62.9660  59.3179  1.00000  0.00000  1.00000  0.39894
50.00000  12.2676  57.2022  49.8793  1.00000  -0.00000  1.00000  0.39894
60.00000  18.4349  52.2388  39.2315  1.00000  -0.00000  1.00000  0.39894
70.00000  26.1183  48.3589  27.2363  1.00000  0.00000  1.00000  0.39894
80.00000  35.1489  45.8640  14.0019  1.00000  0.00000  1.00000  0.39894
90.00000  45.0000  45.0000   0.0000  1.00000  0.00000  1.00000  0.39894

```
