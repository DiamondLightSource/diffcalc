Diffcalc - A Diffraction Condition Calculator for Diffractometer Control
========================================================================

Diffcalc is a python/jython based diffraction condition calculator used for
controlling diffractometers within reciprocal lattice space. It performs the
same task as the fourc, sixc, twoc, kappa, psic and surf macros from SPEC.

There is a `PDF user
manual<https://media.readthedocs.org/pdf/diffcalc/latest/diffcalc.pdf>` and an
online version including a development guide at
`https://diffcalc.readthedocs.io`.

.. contents::

.. section-numbering::

Software compatibility
----------------------

- Written in Python using numpy
- Works in Jython using Jama
- Runs directly in `OpenGDA<http://www.opengda.org>`
- Runs in in Python or IPython using minimal OpenGda emulation (included)
- Contact us for help running in your environment

Diffractometer compatibility
----------------------------

Diffcalc’s standard calculation engine is an implementation of [You1999]_ and
[Busing1967]_. Diffcalc works with any diffractometer which is a subset of:

 .. image:: https://raw.githubusercontent.com/DiamondLightSource/diffcalc/master/doc/source/youmanual/images/4s_2d_diffractometer.png
     :alt: 4s + 2d six-circle diffractometer, from H.You (1999)
     :width: 50%
     :align: center


Diffcalc can be configured to work with any diffractometer geometry which is a
subset of this. For example, a five-circle diffractometer might be missing the
nu circle above.

Note that the first versions of Diffcalc were based on [Vlieg1993]_ and
[Vlieg1998]_ and a ‘Vlieg’ engine is still available.  There is also an engine
based on [Willmott2011]_. The ‘You’ engine is more generic and the plan is to
remove the old ‘Vlieg’ engine once beamlines have been migrated.

Installation
------------

Check it out::

   $ git clone https://github.com/DiamondLightSource/diffcalc.git
   Cloning into 'diffcalc'...

At Diamond Diffcalc may be installed within an OpenGDA deployment and is
available via the 'module' system from bash.

Starting
--------

Start diffcalc in ipython using a sixcircle dummy diffractometer::

   $ cd diffcalc
   $ ./diffcalc.py --help
   ...

   $ ./diffcalc.py sixcircle

   Running: "ipython --no-banner --HistoryManager.hist_file=/tmp/ipython_hist_zrb13439.sqlite -i -m diffcmd.start sixcircle False"

   ---------------------------------- DIFFCALC -----------------------------------
   Startup script: '/Users/zrb13439/git/diffcalc/startup/sixcircle.py'
   Loading ub calculation: 'test'
   ------------------------------------ Help -------------------------------------
   Quick:  https://github.com/DiamondLightSource/diffcalc/blob/master/README.rst
   Manual: https://diffcalc.readthedocs.io
   Type:   > help ub
           > help hkl
   -------------------------------------------------------------------------------
   In [1]:

Within Diamond use::

   $ module load diffcalc
   $ diffcalc --help
   ...
   $ diffcalc sixcircle

Trying it out
-------------

Type ``demo.all()`` to see it working and then move try the following quick
start guide::

   >>> demo.all()
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
See the full `user manual<https://diffcalc.readthedocs.io`> for many more
options and an explanation of what this all means.

To load the last used UB-calculation::

   >>> lastub
   Loading ub calculation: 'mono-Si'

To load a previous UB-calculation::

   >>> listub
   UB calculations in: /Users/walton/.diffcalc/i16

   0) mono-Si            15 Feb 2017 (22:32)
   1) i16-32             13 Feb 2017 (18:32)

   >>> loadub 0

To create a new UB-calculation::

   >>> newub 'example'
   >>> setlat '1Acube' 1 1 1 90 90 90

Find U matrix from two reflections::

   >>> pos wl 1
   wl:        1.0000
   >>> c2th [0 0 1]
   59.99999999999999

   >>> pos sixc [0 60 0 30 90 0]
   sixc:     mu:  0.0000 delta:  60.0000 gam:  0.0000 eta:  30.0000 chi:  90.0000 phi:  0.0000 
   >>> addref [0 0 1]

   >>> pos sixc [0 90 0 45 45 90]
   sixc:     mu:  0.0000 delta:  90.0000 gam:  0.0000 eta:  45.0000 chi:  45.0000 phi:  90.0000 
   >>> addref [0 1 1]
   Calculating UB matrix.


Check that it looks good::

   >>> checkub
   
        ENERGY     H     K     L    H_COMP   K_COMP   L_COMP     TAG
    1  12.3984  0.00  0.00  1.00    0.0000   0.0000   1.0000        
    2  12.3984  0.00  1.00  1.00    0.0000   1.0000   1.0000        

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

Setting the reference vector
----------------------------
See the full `user manual<https://diffcalc.readthedocs.io`> for many more
options and an explanation of what this all means.

By default the reference vector is set parallel to the phi axis. That is,
along the z-axis of the phi coordinate frame.

The `ub` command shows the current reference vector, along with any inferred
miscut, at the top its report (or it can be shown by calling ``setnphi`` or
``setnhkl'`` with no args)::

   >>> ub
   ...
   n_phi:      0.00000   0.00000   1.00000 <- set
   n_hkl:     -0.00000   0.00000   1.00000
   miscut:     None
   ...

Constraining solutions for moving in hkl space
----------------------------------------------
See the full `user manual<https://diffcalc.readthedocs.io`> for many more
options and an explanation of what this all means.

To get help and see current constraints::

   >>> help con
   ...

   >>> con
       DET        REF        SAMP
       ------     ------     ------
       delta  --> a_eq_b --> mu
   --> gam        alpha      eta
       qaz        beta       chi
       naz        psi        phi
                             mu_is_gam
   
       gam  : 0.0000
       a_eq_b
       mu   : 0.0000
   
       Type 'help con' for instructions

Three constraints can be given: zero or one from the DET and REF columns and the
remainder from the SAMP column. Not all combinations are currently available.
Use ``help con`` to see a summary if you run into troubles.

To configure four-circle vertical scattering::

   >>> con gam 0 mu 0 a_eq_b
       gam  : 0.0000
       a_eq_b
       mu   : 0.0000

Moving in hkl space
-------------------

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
   sixc:     mu:  0.0000 delta:  90.0000 gam:  0.0000 eta:  45.0000 chi:  45.0000 phi:  90.0000 


Scanning in hkl space
---------------------

Scan an hkl axis (and read back settings)::

   >>> scan l 0 1 .2 sixc
         l       mu     delta      gam       eta      chi       phi
   -------  -------  --------  -------  --------  -------  --------
   0.00000   0.0000   60.0000   0.0000   30.0000   0.0000   90.0000
   0.20000   0.0000   61.3146   0.0000   30.6573   11.3099   90.0000
   0.40000   0.0000   65.1654   0.0000   32.5827   21.8014   90.0000
   0.60000   0.0000   71.3371   0.0000   35.6685   30.9638   90.0000
   0.80000   0.0000   79.6302   0.0000   39.8151   38.6598   90.0000
   1.00000   0.0000   90.0000   0.0000   45.0000   45.0000   90.0000

Scan a constraint (and read back virtual angles and eta)::

   >>> con psi
       gam  : 0.0000
   !   psi  : ---
       mu   : 0.0000
   >>> scan psi 70 110 10 hklverbose [0 1 1] eta
        psi       eta        h        k        l     theta       qaz     alpha       naz       tau       psi      beta
   --------  --------  -------  -------  -------  --------  --------  --------  --------  --------  --------  --------
   70.00000   26.1183  0.00000  1.00000  1.00000  45.00000  90.00000  19.20748  45.28089  45.00000  70.00000  42.14507
   80.00000   35.1489  -0.00000  1.00000  1.00000  45.00000  90.00000  24.40450  40.12074  45.00000  80.00000  35.93196
   90.00000   45.0000  0.00000  1.00000  1.00000  45.00000  90.00000  30.00000  35.26439  45.00000  90.00000  30.00000
   100.00000   54.8511  -0.00000  1.00000  1.00000  45.00000  90.00000  35.93196  30.68206  45.00000  100.00000  24.40450
   110.00000   63.8817  -0.00000  1.00000  1.00000  45.00000  90.00000  42.14507  26.34100  45.00000  110.00000  19.20748

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
