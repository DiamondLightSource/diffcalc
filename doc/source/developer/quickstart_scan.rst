.. _quickstart-scan:

Quick-Start: Scanning
=====================

This section describes how to start Diffcalc in Python in a way that
provides a scan command and that also exposes user-level commands to
the root namespace. This does not provide motor control, but does
provide dummy software motor objects that could be easily replaced
with real implementations for EPICS or TANGO for example. The dummy
software objects operate through a Scannable interface compatable
with the OpenGDA's. gda.device.Scannable interface.

For a full description of what Diffcalc does and how to use it please
see the 'Diffcalc user manual'.


Introduction to Scannables
--------------------------
Scannables are objects that can be operated by a scan or pos command.


Setup environment
-----------------

.. include:: quickstart_setup_environment

Start
-----

With Python start the sixcircle_api.py example startup script (notice
the -i and -m) and type ``demo_all()``::

   $ python -i -m example/startup/sixcircle
   >>> demo_all()
   >>> demo_scan()

Or with IPython::

   $ ipython -i example/startup/sixcircle.py
   >>> demo_all()
   >>> demo_scan()

Alternatively start Python or IPython and cut and paste lines from the rest of
this tutorial::

   $ python
   $ ipython


Configure a diffraction calculator and Scannables
-------------------------------------------------

Create some dummy motor Scannables and an energy Scannable::

   >>> from diffcalc.gdasupport.minigda.scannable import SingleFieldDummyScannable
   >>> mu = SingleFieldDummyScannable('mu')
   >>> delta = SingleFieldDummyScannable('delta')
   >>> nu = SingleFieldDummyScannable('nu')
   >>> eta = SingleFieldDummyScannable('eta')
   >>> chi = SingleFieldDummyScannable('chi')
   >>> phi = SingleFieldDummyScannable('phi')
   
   >>> en = SingleFieldDummyScannable('en')

Increase the priority of the energy scnannable so that it will be
moved before ``hkl`` in scans (see below).

   >>> en.level = 3

Build a Diffcalc calculator and associated Scannables and
user-level commands::

   >>> from diffcalc.gdasupport.factory import create_objects
  
   >>> virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
   >>> _objects = create_objects(
          engine_name='you',
          geometry='sixc',
          axis_scannable_list=(mu, delta, nu, eta, chi, phi),
          energy_scannable=en,
          hklverbose_virtual_angles_to_report=virtual_angles,
          simulated_crystal_counter_name='ct')

Add these to the root namespace for easy interactive use::

   >>> from diffcalc.gdasupport.factory impor add_objects_to_namespace
   >>> add_objects_to_namespace(_objects, globals())
   >>> ===============================================================
   >>> Added objects/methods to namespace:
   >>> addref, alpha, beta, c2th, calcub, checkub, chi_par, con,
   >>> ct, dc, delref, delta_par, editref, eta_par, h, hardware, hkl,
   >>> hklverbose, k, l, listub, loadub, mu_par, naz, newub, nu_par,
   >>> phi_par, psi, qaz, saveubas, setcut, setlat, setmax, setmin,
   >>> setu, setub, showref, sigtau, sim, sixc, swapref, trialub, ub,
   >>> uncon, wl
   >>> ===============================================================

(This is equivilent to ``globals().extend(_objects)`` but checks for
namespace collisions and does some reporting.)

Import pos and scan commands
----------------------------

To create a pos command for moving Scannables and a scan command for
scannig them::

   >>> from diffcalc.gdasupport.minigda import command
   >>> pos = command.Pos(globals())
   >>> scan = command.Scan(command.ScanDataPrinter())

Introduction to pos and scan
----------------------------

The pos command can be used to check the position of all scannables::

   >>> pos()
   sixc:     mu: 0.0 delta: 0.0 nu: 0.0 eta: 0.0 chi: 0.0 phi: 0.0 
   alpha:    Error: alpha
   ...

To check the position of a single scannable::

   >>> pos(phi)
   phi: 0.0
    
   >>> phi                               # alternatively
   phi: 0.0
   
   >>> phi() + 100                       # call to get number
   100

To move a scannable::

   >>> pos(phi, 5)
   phi:      5.0000


To perform a basic (and not very useful) scan for example::

   >>> scan(phi, 0, 50, 10, chi, 5, eta)
   Fri Mar 16 10:02:37 2012
   ================
        phi    delta	
    -------  -------
     0.0000  0.0000	
     0.0000  0.0000	
    20.0000  0.0000	
    30.0000  0.0000	
    40.0000  0.0000	
    ================


Getting help
------------

To get help for the orientation phase, the angle calculation phase,
and the dummy hardware adapter commands::

   >>> help(ub)
   >>> help(hkl)

Orientation
-----------

To orient the crystal for example (see the user manual for a fuller
tutorial) first find some reflections::

   >>> # Create a new ub calculation and set lattice parameters
   >>> newub('test')
   >>> setlat('cubic', 1, 1, 1, 90, 90, 90)
   
   >>> # Add 1st reflection
   >>> pos(wl, 1)
   >>> c2th([1, 0, 0])
   60.
   >>> pos(sixc, [0, 60, 0, 30, 0, 0])
   sixc:     mu: 0.0 delta: 60.0 nu: 0.0 eta: 30.0 chi: 0.0 phi: 0.0 
   >>> addref([1, 0, 0])

   >>> # Add 2nd reflection
   >>> pos(phi, 90)
   >>> addref([0, 1, 0])
   Calculating UB matrix.

To check the state of the current UB calculation::

   >>> ub()
   
   UBCALC

      name:          test
   
   CRYSTAL

      name:         cubic

      a, b, c:    1.00000   1.00000   1.00000
                 90.00000  90.00000  90.00000

      B matrix:   6.28319   0.00000   0.00000
                  0.00000   6.28319   0.00000
                  0.00000   0.00000   6.28319

   UB MATRIX
   
      U matrix:   1.00000   0.00000   0.00000
                  0.00000   1.00000   0.00000
                  0.00000   0.00000   1.00000

      UB matrix:  6.28319   0.00000   0.00000
                  0.00000   6.28319   0.00000
                  0.00000   0.00000   6.28319

   REFLECTIONS

        ENERGY     H     K     L       MU   DELTA      NU     ETA     CHI     PHI  TAG
      1 12.398  1.00  0.00  0.00   0.0000 60.0000  0.0000 30.0000  0.0000  0.0000
      2 12.398  0.00  1.00  0.00   0.0000 60.0000  0.0000 30.0000  0.0000 90.0000  


And finally to check the reflections were specified acurately::

   >>> checkub()
        ENERGY     H     K     L   H_COMP  K_COMP  L_COMP     TAG
    1  12.3984  1.00  0.00  0.00   1.0000  0.0000  0.0000        
    2  12.3984  0.00  1.00  0.00   0.0000  1.0000  0.0000        

Motion
------

Hkl positions and virtual angles can now be read up from angle
settings (the easy direction!)::

   >>> pos(hkl)
   hkl:      h: 0.00000 k: 1.00000 l: 0.00000 
   
   >>> pos(hklverbose)
   hklverbose: h: 0.00000 k: 1.00000 l: 0.00000
               theta: 30.00000 qaz: 90.00000 alpha: -0.00000 naz: 0.00000
               tau: 90.00000 psi: 90.00000 beta: 0.00000 

 
Before calculating the settings to reach an hkl position (the trickier
direction) hardware limits must be set and combination of constraints
chosen. The constraints here result in a four circle like mode with a
vertical scattering plane and incident angle 'alpha' equal to the exit
angle 'beta'::

   >>> con(qaz, 90)
   !   2 more constraints required
       qaz: 90.0000
    
   >>> con(a_eq_b)
   !   1 more constraint required
       qaz: 90.0000
       a_eq_b
   
   >>> con(mu, 0)
       qaz: 90.0000
       a_eq_b
       mu: 0.0000

To check the constraints::
   
    >>> con()
        DET        REF        SAMP
        ======     ======     ======
        delta  --> a_eq_b --> mu
        alpha      eta
    --> qaz        beta       chi
        naz        psi        phi
                             mu_is_nu
   
        qaz: 90.0000
        a_eq_b
        mu: 0.0000
   
        Type 'help con' for instructions

Limits can be set to help (or in somfe cases alow) Diffcalc choose a
solution::
  
    >>> setmin(delta, 0)
    >>> setmin(chi, 0)

The hkl scannable can now be moved which will in turn move sixc and the
underlying motors mu, delta, nu, eta, chi and phi::

   >>> pos(hkl,dd [1, 0, 0])
   hkl:      h: 1.00000 k: 0.00000 l: 0.00000 
     
   >>> sixc
  
   sixc:
        mu :    0.0
     delta :   60.0
        nu :    0.0
       eta :   30.0
       chi :    0.0
       phi :    0.0
   
   >>> hkl
   hkl:
       hkl :    1.0000  0.0000  0.0000
     alpha :    0.0
      beta :    0.0
       naz :    0.0
       psi :   90.0
       qaz :   90.0
       tau :   90.0
     theta :   30.0

Alternatively h, k and l can moved::

   >>> pos(k, 1)
   k:        1.00000
   
   >>> hkl
 
   hkl:
       hkl :    1.0000  1.0000  0.0000
     alpha :   -0.0
      beta :    0.0
       naz :    0.0
       psi :   90.0
       qaz :   90.0
       tau :   90.0
     theta :   45.0

Scanning
--------

Scannables can be moved in very generic ways to construct many types
of scan.

Scan delta through hkl=100 while counting a counter timer, ct, for 1s
and reporting the resulting hkl position::

    >>> pos(hkl, [1, 0, 0])
    hkl:      h: 1.00000 k: 0.00000 l: 0.00000 

    >>> scan(delta, 40, 80, 10, hkl, ct, 1)
   
    -------  -------  -------  -------  -------
      delta        h        k        l       ct
    -------  -------  -------  -------  -------
    40.0000  0.67365  0.11878  0.00000  0.00959
    50.0000  0.84202  0.07367  0.00000  0.87321
    60.0000  1.00000  0.00000  0.00000  3.98942
    70.0000  1.14279 -0.09998  0.00000  0.87321
    80.0000  1.26604 -0.22324  0.00000  0.00959

Scan h from hkl=010 to hkl=110 while counting a counter timer for 1s
and reporting h and l and all the axes postions::

    >>> pos(hkl, [0, 1, 0])
    hkl:      h: -0.00000 k: 1.00000 l: 0.00000 
   
    >>> scan(h, 0, 1, .2, k, l, sixc, ct, 1)
 
    --------  -------  -------  ------  -------  ------  -------  ------  -------  -------
           h        k        l      mu    delta      nu      eta     chi      phi       ct
    --------  -------  -------  ------  -------  ------  -------  ------  -------  -------
     0.00000  1.00000  0.00000  0.0000  60.0000  0.0000  30.0000  0.0000  90.0000  3.98942
     0.20000  1.00000  0.00000  0.0000  61.3146  0.0000  30.6573  0.0000  78.6901  0.53991
     0.40000  1.00000  0.00000  0.0000  65.1654  0.0000  32.5827  0.0000  68.1986  0.00134
     0.60000  1.00000  0.00000  0.0000  71.3371  0.0000  35.6685  0.0000  59.0362  0.00134
     0.80000  1.00000  0.00000  0.0000  79.6302  0.0000  39.8151  0.0000  51.3402  0.53991
     1.00000  1.00000  0.00000  0.0000  90.0000  0.0000  45.0000  0.0000  45.0000  3.98942

Rotate about the hkl=101 reflection while counting a counter timer for
.1s and reporting the three unconstraied sample angles::

   >>> con(psi)
       qaz: 90.0000
   !   psi: ---
       mu: 0.0000
 
   >>> scan(psi, 0, 90, 10, hkl, [1, 0, 1], eta, chi, phi, ct, .1)
 
        psi     eta      chi      phi        h        k        l       ct
    -------   ------  -------  -------  -------  -------  -------  -------
    0.00000   0.0000  90.0000  90.0000  1.00000  0.00000  1.00000  0.39894
   10.00000   0.4385  82.9470  82.8929  1.00000  0.00000  1.00000  0.39894
   20.00000   1.7808  76.0046  75.5672  1.00000  0.00000  1.00000  0.39894
   30.00000   4.1066  69.2952  67.7923  1.00000  0.00000  1.00000  0.39894
   40.00000   7.5463  62.9660  59.3179  1.00000  0.00000  1.00000  0.39894
   50.00000  12.2676  57.2022  49.8793  1.00000  0.00000  1.00000  0.39894
   60.00000  18.4349  52.2388  39.2315  1.00000  0.00000  1.00000  0.39894
   70.00000  26.1183  48.3589  27.2363  1.00000  0.00000  1.00000  0.39894
   80.00000  35.1489  45.8640  14.0019  1.00000  0.00000  1.00000  0.39894
   90.00000  45.0000  45.0000   0.0000  1.00000  0.00000  1.00000  0.39894
