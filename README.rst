Diffcalc - A Diffraction Condition Calculator for Diffractometer Control
========================================================================

Diffcalc is a python/jython based diffraction condition calculator used for
controlling diffractometers within reciprocal lattice space. It performs the
same task as the fourc, sixc, twoc, kappa, psic and surf macros from SPEC.

Diffcalc’qs standard calculation engine is an implementation of [You1999]_ . The
first versions of Diffcalc were based on [Vlieg1993]_ and [Vlieg1998]_ and a
‘Vlieg’ engine is still available. The ‘You’ engine is more generic and the plan
is to remove the old ‘Vlieg’ engine once beamlines have been migrated. New users
should use the ‘You’ engine. There is also an engine based on [Willmott2011]_.

The foundations for this type of calculation were laid by by Busing & Levi in
their classic paper [Busing1967]_. Diffcalc’s orientation algorithm is taken from
this paper. Busing & Levi also provided the original definition of the
coordinate frames and of the U and B matrices used to describe a crystal’s
orientation and to convert between Cartesian and reciprical lattice space.

Geometry plugins are used to adapt the six circle model used internally by
Diffcalc to apply to other diffractometers. These contain a dictionary of the
‘missing’ angles which Diffcalc uses to constrain these angles internally, and a
methods to map from external angles to Diffcalc angles and visa versa.

Installing and starting
-----------------------

Diffcalc depends on numpy and, when used outside Diamond's opengda framework (as
here), works best with ipython.

Check it out::

   $ git clone https://github.com/DiamondLightSource/diffcalc.git
   Cloning into 'diffcalc'...

Start diffcalc in ipython using a sixcircle dummy diffractometer::

   $ cd diffcalc
   $ ./diffcalc.py --help
   ...
   $ ./diffcalc.py sixcircle
   Running command: 'ipython --HistoryManager.hist_file=/tmp/ipython_hist_walton.sqlite -i -m diffcmd.start sixcircle False
   -------------------------------------------------------------------------------
   Executing startup script: '/Users/walton/git/diffcalc/startup/sixcircle.py'
   Dummy scannables: sixc(mu, delta, gam, eta, chi, phi) and en
   Falling back to the (very minimal!) minigda...
   -------------------------------------------------------------------------------
   In [1]:

NOTE: Within Diamond use::

   $ module load diffcalc
   $ diffcalc --help
   ...
   $ diffcalc sixcircle

Type ``demo_all()`` to see it working and then move try the following quick
start guide::

   >>> demo_all()
   ...

Getting help
------------

To view help with orientation and then moving in hkl space::

   >>> help ub
   ...
   >>> help hkl
   ...

Configuring a UB calculation
----------------------------

To load the last used UB-calculation::

   >>> lastub
   Loading ub calculation: 'mono-Si'

To load a previous UB-calculation::

   >>> listub
   UB calculations in: /Users/walton/.diffcalc/i16

   0) mono-Si            15 Feb 2017 (22:32)
   1) i16-32          13 Feb 2017 (18:32)

   >>> loadub 0

To create a new UB-calculation::

   >>> newub 'example'
   >>> setlat '1Acube' 1 1 1 90 90 90

Find U matrix from two reflections::

   >>> pos wl 1
   wl:       1.0000
   >>> c2th [0 0 1]
   59.99999999999999

   >>> pos sixc [0 60 0 30 90 0]
   sixc:     mu: 0.0000 delta: 60.0000 gam: 0.0000 eta: 30.0000 chi: 90.0000 phi: 0.0000 
   >>> addref [0 0 1]

   >>> pos sixc [0 90 0 45 45 90]
   sixc:     mu: 0.0000 delta: 90.0000 gam: 0.0000 eta: 45.0000 chi: 45.0000 phi: 90.0000 
   >>> addref [0 1 1]
   Calculating UB matrix.

   >>> checkub
   
        ENERGY     H     K     L    H_COMP   K_COMP   L_COMP     TAG
    1  12.3984  0.00  0.00  1.00    0.0000   0.0000   1.0000        
    2  12.3984  0.00  1.00  1.00    0.0000   1.0000   1.0000        

Set U matrix manually (pretending sample is squarely mounted)::

   >>> setu [[1 0 0] [0 1 0] [0 0 1]]
   Recalculating UB matrix.
   NOTE: A new UB matrix will not be automatically calculated when the orientation reflections are modified.

To estimate based on first reflection only::

   >>> trialub
   resulting U angle: 0.00000 deg
   resulting U axis direction: [-1.00000,  0.00000,  0.00000]
   Recalculating UB matrix from the first reflection only.
   NOTE: A new UB matrix will not be automatically calculated when the orientation reflections are modified.

To see the resulting UB-calculation::

   >>> ub
   UBCALC
   
      name:       example
   
      n_phi:      0.00000   0.00000   1.00000 <- set
      n_hkl:     -0.00000   0.00000   1.00000
      miscut:     None
   
   CRYSTAL
   
      name:        1Acube
   
      a, b, c:    1.00000   1.00000   1.00000
                 90.00000  90.00000  90.00000
   
      B matrix:   6.28319   0.00000   0.00000
                  0.00000   6.28319   0.00000
                  0.00000   0.00000   6.28319
   
   UB MATRIX
   
      U matrix:   1.00000   0.00000   0.00000
                  0.00000   1.00000   0.00000
                  0.00000   0.00000   1.00000
   
      U angle:    0
   
      UB matrix:  6.28319   0.00000   0.00000
                  0.00000   6.28319   0.00000
                  0.00000   0.00000   6.28319
   
   REFLECTIONS
   
        ENERGY     H     K     L        MU    DELTA      GAM      ETA      CHI      PHI  TAG
      1 12.398  0.00  0.00  1.00    0.0000  60.0000   0.0000  30.0000  90.0000   0.0000  
      2 12.398  0.00  1.00  1.00    0.0000  90.0000   0.0000  45.0000  45.0000  90.0000  

Constraining solutions for moving in hkl space
----------------------------------------------

To get help and see current constraints::

   >>> help con
   ...

   >>> con
       DET        REF        SAMP
       ======     ======     ======
       delta      a_eq_b     mu
       gam        alpha      eta
       qaz        beta       chi
       naz        psi        phi
                             mu_is_gam
   
   !   3 more constraints required
   
       Type 'help con' for instructions

Three constraints can be given: zero or one from the DET and REF columns and the
remainder from the SAMP column. Not all combinations are currently available.
Use ``help con`` to see a summary if you run into troubles.

In the following, the *scattering plane* is defined as the plane including the
scattering vector , or momentum transfer vector, and the incident beam.

**DET:** (detector)

- **delta** - physical delta setting (vertical detector rotation). *del=0 is equivalent to qaz=0*
- **gam** - physical gamma setting (horizontal detector rotation). *gam=0 is equivalent to qaz=90*
- **qaz** - azimuthal rotation of scattering vector (about the beam, from horizontal)
- **qaz** - azimuthal rotation of reference vector (about the beam, from horizontal)

**REF:**

- **alpha** - incident angle to surface (if reference is normal to surface)
- **beta** -  exit angle from surface (if reference is normal to surface)
- **psi** - azimuthal rotation about scattering vector of reference vector (from scattering plane)
- **a_eq_b** - bisecting mode with alpha=beta. *Equivalent to psi=90*

**SAMP:**

- **mu, eta, chi & phi** - physical settings
- **mu_is_gam** - force mu to follow gamma (results in a 5-circle geometry)

Diffcalc will report two other (un-constrainable) virtual angles:

- **theta** - half of 2theta, the angle through the diffracted beam bends
- **tau** - longitude of reference vector from scattering vector (in scattering plane)

Example constraint modes
------------------------

Vertical four circle mode::

   >>> con gam 0 mu 0 a_eq_b   # or equivalently:
   >>> con qaz 90 mu 0 a_eq_b

   >>> con alpha 1             # replaces a_eq_b

Horizontal four circle mode::

   >>> con del 0 eta 0 alpha 1   # or equivalently:
   >>> con qaz 0 mu 0 alpha 1

Surface vertical mode::

   >>> con naz 90 mu 0 alpha 1

Surface horizontal mode::

   >>> con naz 0 eta 0 alpha 1

Moving in hkl space
-------------------

Configure a mode, e.g. four-circle vertical::

   >>> con gam 0 mu 0 a_eq_b
       gam: 0.0000
       a_eq_b
       mu: 0.0000

Simulate moving to a reflection::

   >>> sim hkl [0 1 1]
   sixc would move to:
        mu :    0.0000
     delta :   90.0000
       gam :    0.0000
       eta :   45.0000
       chi :   45.0000
       phi :   90.0000
   
     alpha :   30.0000
      beta :   30.0000
       naz :   35.2644
       psi :   90.0000
       qaz :   90.0000
       tau :   45.0000
     theta :   45.0000

Move to reflection::

   >>> pos hkl [0 1 1]
   hkl:      h: 0.00000 k: 1.00000 l: 1.00000 

   >>> pos sixc
   sixc:     mu: 0.0000 delta: 90.0000 gam: 0.0000 eta: 45.0000 chi: 45.0000 phi: 90.0000 

Scan an hkl axis (and read back settings)::

   >>> scan l 0 1 .2 sixc
         l      mu    delta     gam      eta     chi      phi
   -------  ------  -------  ------  -------  ------  -------
   0.00000  0.0000  60.0000  0.0000  30.0000  0.0000  90.0000
   0.20000  0.0000  61.3146  0.0000  30.6573  11.3099  90.0000
   0.40000  0.0000  65.1654  0.0000  32.5827  21.8014  90.0000
   0.60000  0.0000  71.3371  0.0000  35.6685  30.9638  90.0000
   0.80000  0.0000  79.6302  0.0000  39.8151  38.6598  90.0000
   1.00000  0.0000  90.0000  0.0000  45.0000  45.0000  90.0000

Scan a constraint (and read back virtual angles and eta)::

   >>> con psi
       gam: 0.0000
   !   psi: ---
       mu: 0.0000
   >>> scan psi 70 110 10 hklverbose [0 1 1] eta
        psi      eta         h        k        l     theta       qaz     alpha       naz       tau       psi      beta
   --------  -------  --------  -------  -------  --------  --------  --------  --------  --------  --------  --------
   70.00000  26.1183  -0.00000  1.00000  1.00000  45.00000  90.00000  19.20748  45.28089  45.00000  70.00000  42.14507
   80.00000  35.1489  -0.00000  1.00000  1.00000  45.00000  90.00000  24.40450  40.12074  45.00000  80.00000  35.93196
   90.00000  45.0000   0.00000  1.00000  1.00000  45.00000  90.00000  30.00000  35.26439  45.00000  90.00000  30.00000
   100.00000  54.8511  -0.00000  1.00000  1.00000  45.00000  90.00000  35.93196  30.68206  45.00000  100.00000  24.40450
   110.00000  63.8817  -0.00000  1.00000  1.00000  45.00000  90.00000  42.14507  26.34100  45.00000  110.00000  19.20748

References
----------

.. [You1999] H. You. *Angle calculations for a '4S+2D' six-circle diffractometer.*
   J. Appl. Cryst. (1999). **32**, 614-623. `(pdf link)
   <http://journals.iucr.org/j/issues/1999/04/00/hn0093/hn0093.pdf>`__.

.. [Busing1967] W. R. Busing and H. A. Levy. *Angle calculations for 3- and 4-circle X-ray
   and neutron diffractometers.* Acta Cryst. (1967). **22**, 457-464. `(pdf link)
   <http://journals.iucr.org/q/issues/1967/04/00/a05492/a05492.pdf>`__.

.. [Vlieg1993] Martin Lohmeier and Elias Vlieg. *Angle calculations for a six-circle
   surface x-ray diffractometer.* J. Appl. Cryst. (1993). **26**, 706-716. `(pdf link)
   <http://journals.iucr.org/j/issues/1993/05/00/la0044/la0044.pdf>`__.

.. [Vlieg1998] Elias Vlieg. *A (2+3)-type surface diffractometer: mergence of the z-axis and
   (2+2)-type geometries.* J. Appl. Cryst. (1998). **31**, 198-203. `(pdf link)
   <http://journals.iucr.org/j/issues/1998/02/00/pe0028/pe0028.pdf>`__.

.. [Willmott2011] C. M. Schlepütz, S. O. Mariager, S. A. Pauli, R. Feidenhans'l and
   P. R. Willmott. *Angle calculations for a (2+3)-type diffractometer: focus
   on area detectors.* J. Appl. Cryst. (2011). **44**, 73-83. `(pdf link)
   <http://journals.iucr.org/j/issues/2011/01/00/db5088/db5088.pdf>`__.
