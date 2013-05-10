.. _quickstart-api:

Quick-Start: Python API
=======================

This section describes how to run up only the core in Python or
IPython.  Starting diffcalc without the additional functionality
described in :ref:`quickstart-scan` or :ref:`quickstart-opengda`
provides a good way to understand how the code is structured.  It also
provides an API which could be used to integrate Diffcalc into an
existing data acquisition system; although the interface described in
:ref:`quickstart-scan` would normally provide a better starting point.

For a full description of what Diffcalc does and how to use it please
see the 'Diffcalc user manual'.

Setup environment
-----------------

.. include:: quickstart_setup_environment


Start
-----

With Python start the sixcircle_api.py example startup script (notice
the -i and -m) and type ``demo_all()``::

   $ python -i -m example/startup/sixcircle_api
   >>> demo_all()

Or with IPython::

   $ ipython -i example/startup/sixcircle_api.py
   >>> demo_all()

Alternatively start Python or IPython and cut and paste lines from the rest of
this tutorial::

   $ python
   $ ipython

Configure a diffraction calculator
----------------------------------

To setup a Diffcalc calculator::

   >>> from diffcalc.hkl.you.geometry import SixCircle
   >>> from diffcalc.hardware import DummyHardwareAdapter
   >>> from diffcalc.diffcalc_ import create_diffcalc

   >>> hardware = DummyHardwareAdapter(('mu', 'delta', 'nu', 'eta', 'chi', 'phi'))
   >>> dc = create_diffcalc('you', SixCircle(), hardware)

The hardware adapter is used by Diffcalc to read up the current angle
settings, wavelength and axes limits. It is primarily used to simplify
commands for end users. It could be dropped for this API use, but it
is also used for the important job of checking axes limits while
choosing solutions.

Geometry plugins are used to adapt the six circle model used
internally by Diffcalc to apply to other diffractometers. These
contain a dictionary of the 'missing' angles which Diffcalc internally
uses to constrain these angles, and a methods to map from
external angles to Diffcalc angles and visa versa.

Getting help
------------

To get help for the orientation phase, the angle calculation phase,
and the dummy hardware adapter commands::

   >>> help(dc.ub)
   >>> help(dc.hkl)
   >>> help(hardware)

Orientation
-----------

To orient the crystal for example (see the user manual for a fuller
tutorial) first find some reflections::

   >>> # Create a new ub calculation and set lattice parameters
   >>> dc.ub.newub('test')
   >>> dc.ub.setlat('cubic', 1, 1, 1, 90, 90, 90)
   
   >>> # Add 1st reflection
   >>> dc.ub.c2th([1, 0, 0])                      # energy from hardware
   60.
   >>> hardware.position = 0, 60, 0, 30, 0, 0     # mu del nu eta chi phi
   >>> dc.ub.addref([1, 0, 0])                    # energy and pos from hardware

   >>> # Add 2nd reflection
   >>> dc.ub.addref([0, 1, 0], [0, 60, 0, 30, 0, 90], en)
   Calculating UB matrix.

To check the state of the current UB calculation::

   >>> dc.ub.ub()
   
   UBCALC

      name:          test
   
   CRYSTAL

      name:         cubic

      a, b, c:    1.00000   1.00000   1.00000
                 90.00000  90.00000  90.00000

      B matrix:   6.28319  -0.00000  -0.00000
                  0.00000   6.28319  -0.00000 0.00000   0.00000 6.28319

   UB MATRIX
   
      U matrix:   1.00000   0.00000   0.00000
                 -0.00000   1.00000   0.00000
                  0.00000   0.00000   1.00000

      UB matrix:  6.28319  -0.00000  -0.00000
                 -0.00000   6.28319  -0.00000
                  0.00000   0.00000   6.28319

   REFLECTIONS

        ENERGY     H     K     L       MU   DELTA      NU     ETA     CHI     PHI  TAG
      1 12.398  1.00  0.00  0.00   0.0000 60.0000  0.0000 30.0000  0.0000  0.0000
      2 12.398  0.00  1.00  0.00   0.0000 60.0000  0.0000 30.0000  0.0000 90.0000  


And finally to check the reflections were specified acurately::

   >>> dc.checkub()
        ENERGY     H     K     L   H_COMP  K_COMP  L_COMP     TAG
    1  12.3984  1.00  0.00  0.00   1.0000  0.0000  0.0000        
    2  12.3984  0.00  1.00  0.00   0.0000  1.0000  0.0000        

Motion
------

Hkl positions and virtual angles can now be read up from angle
settings (the easy direction!)::

   >>> dc.angles_to_hkl((0., 60., 0., 30., 0., 0.))     # energy from hardware
   ((1., 0.0, 0.0),
    {'alpha': 0.0,
     'beta': 0.0,
     'naz': 0.0,
     'psi': 90.0,
     'qaz': 90.0,
     'tau': 90.0,
     'theta': 29.999999999999996})
 
Before calculating the settings to reach an hkl position (the trickier
direction) hardware limits must be set and combination of constraints
chosen. The constraints here result in a four circle like mode with a
vertical scattering plane and incident angle 'alpha' equal to the exit
angle 'beta'::

    >>> dc.hkl.con('qaz', 90)
   !   2 more constraints required
       qaz: 90.0000
   
    >>> dc.hkl.con('a_eq_b')
   !   1 more constraint required
       qaz: 90.0000
       a_eq_b
   
    >>> dc.hkl.con('mu', 0)
       qaz: 90.0000
       a_eq_b
       mu: 0.0000

To check the constraints::
   
    >>> dc.hkl.con()
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

Limits can be set to help Diffcalc choose a solution::   

    >>> hardware.set_lower_limit('delta', 0)       # used when choosing solution

Angles and virtual angles are then easily determined for a given hkl reflection::

   >>> dc.hkl_to_angles(1, 0, 0)                        # energy from hardware
   ((0.0, 60.0, 0.0, 30.0, 0.0, 0.0),
    {'alpha': -0.0,
     'beta': 0.0,
     'naz': 0.0,
     'psi': 90.0,
     'qaz': 90.0,
     'tau': 90.0,
     'theta': 30.0})



