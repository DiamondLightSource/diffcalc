.. _quickstart-api:

.. warning:: This documentation is out of date. The README and the user doc has been updated recently. For now if you need help with API, please contact me at Diamond. -- Rob Walton

Quick-Start: Python API
=======================

This section describes how to run up only the core in Python or
IPython.  This provides an API which could be used to integrate Diffcalc into an
existing data acquisition system; although the interface described in
the README would normally provide a better starting point.

For a full description of what Diffcalc does and how to use it please
see the 'Diffcalc user manual'.

Setup environment
-----------------

.. include:: quickstart_setup_environment


Start
-----

With Python start the sixcircle_api.py example startup script (notice
the -i and -m) and call `demo_all()`::

   $ python -i -m startup.api.sixcircle
   >>> demo_all()

IPython requires::

   $ ipython -i startup/api/sixcircle.py
   >>> demo_all()

Alternatively start Python or IPython and cut and paste lines from the rest of
this tutorial.

Configure a diffraction calculator
----------------------------------

By default some exceptions are handled in a way to make user interaction
friendlier. Switch this off with::

   >>> import diffcalc.util
   >>> diffcalc.util.DEBUG = True

To setup a Diffcalc calculator, first configure `diffcalc.settings` module::

	>>> from diffcalc import settings
	>>> from diffcalc.hkl.you.geometry import SixCircle
	>>> from diffcalc.hardware import DummyHardwareAdapter
	>>> settings.hardware = DummyHardwareAdapter(('mu', 'delta', 'gam', 'eta', 'chi', 'phi'))
	>>> settings.geometry = SixCircle()  # @UndefinedVariable

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


Calling the API
---------------

The ``diffcalc.dc.dcyou`` module (and others) read the ``diffcalc.settings`` module when first
imported. Note that this means that changes to the settings will most likely
have no effect unless ``diffcalc.dc.dcyou`` is reloaded::

	>>> import diffcalc.dc.dcyou as dc
	
This includes the two critical functions::

	def hkl_to_angles(h, k, l, energy=None):
	    """Convert a given hkl vector to a set of diffractometer angles
	    
	    return angle tuple and virtual angles dictionary
	    """
	
	def angles_to_hkl(angle_tuple, energy=None):
	    """Converts a set of diffractometer angles to an hkl position
	    
	    Return hkl tuple and virtual angles dictionary	    
	    """

``diffcalc.dc.dcyou`` also brings in all the commands from  ``diffcalc.ub.ub``,
``diffcalc.hardware`` and ``diffcalc.hkl.you.hkl``. That is it includes all the
commands exposed in the top level namespace when diffcalc is used interactively::

	>>> dir(dc)
	
	['__builtins__', '__doc__', '__file__', '__name__', '__package__',
	'_hardware','_hkl', '_ub', 'addref', 'allhkl', 'angles_to_hkl', 'c2th',
	'calcub', 'checkub', 'clearref', 'con', 'constraint_manager', 'delref',
	'diffcalc', 'editref', 'energy_to_wavelength', 'hardware', 'hkl_to_angles',
	'hklcalc', 'lastub', 'listub', 'loadub', 'newub', 'rmub', 'saveubas', 'setcut',
	'setlat', 'setmax', 'setmin', 'settings', 'setu', 'setub', 'showref',
	'swapref', 'trialub', 'ub', 'ub_commands_for_help', 'ubcalc', 'uncon']

This doesn't form the best API to program against though, so it is best to
use the four modules more directly. The example below assumes you have
also imported::
	
	>>> from diffcalc.ub import ub
	>>> from diffcalc import hardware
	>>> from diffcalc.hkl.you import hkl

Getting help
------------

To get help for the diffcalc angle calculations, the orientation phase, the
angle calculation phase, and the dummy hardware adapter commands::

   >>> help(dc)
   >>> help(ub)
   >>> help(hkl)
   >>> help(hardware)


Orientation
-----------

To orient the crystal for example (see the user manual for a fuller
tutorial) first find some reflections::
    
   # Create a new ub calculation and set lattice parameters
   ub.newub('test')
   ub.setlat('cubic', 1, 1, 1, 90, 90, 90)
		
   # Add 1st reflection (demonstrating the hardware adapter)
   hardware.settings.hardware.wavelength = 1
   ub.c2th([1, 0, 0])                              # energy from hardware
   settings.hardware.position = 0, 60, 0, 30, 0, 0 # mu del nu eta chi ph
   ub.addref([1, 0, 0])                            # energy & pos from hardware
	
   # Add 2nd reflection (this time without the hardware adapter)
   ub.c2th([0, 1, 0], 12.39842)
   ub.addref([0, 1, 0], [0, 60, 0, 30, 0, 90], 12.39842)
   

To check the state of the current UB calculation::

   >>> ub.ub()

	UBCALC
	
	   name:          test
	
	   n_phi:      0.00000   0.00000   1.00000 <- set
	   n_hkl:     -0.00000   0.00000   1.00000
	   miscut:     None
	
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
	
	   U angle:    0
	
	   UB matrix:  6.28319   0.00000   0.00000
	               0.00000   6.28319   0.00000
	               0.00000   0.00000   6.28319
	
	REFLECTIONS
	
	     ENERGY     H     K     L        MU    DELTA      GAM      ETA      CHI      PHI  TAG
	   1 12.398  1.00  0.00  0.00    0.0000  60.0000   0.0000  30.0000   0.0000   0.0000  
	   2 12.398  0.00  1.00  0.00    0.0000  60.0000   0.0000  30.0000   0.0000  90.0000  
	
And finally to check the reflections were specified acurately::

   >>> dc.checkub()
   
       ENERGY     H     K     L    H_COMP   K_COMP   L_COMP     TAG
   1  12.3984  1.00  0.00  0.00    1.0000   0.0000   0.0000        
   2  12.3984  0.00  1.00  0.00   -0.0000   1.0000   0.0000 

Motion
------

Hkl positions and virtual angles can now be read up from angle
settings (the easy direction!)::


	>>> dc.angles_to_hkl((0., 60., 0., 30., 0., 0.)) # energy from hardware

	((1.0, 5.5511151231257827e-17, 0.0),
	{'alpha': -0.0,
	 'beta': 3.5083546492674376e-15,
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

   >>> hkl.con('qaz', 90)
   !   2 more constraints required
       qaz: 90.0000

   >>> hkl.con('a_eq_b')
   !   1 more constraint required
       qaz: 90.0000
       a_eq_b

   >>> hkl.con('mu', 0)
       qaz: 90.0000
       a_eq_b
       mu: 0.0000

To check the constraints::

   >>> hkl.con()
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

    >>> hardware.setmin('delta', 0)       # used when choosing solution

Angles and virtual angles are then easily determined for a given hkl reflection::

   >>> dc.hkl_to_angles(1, 0, 0)                        # energy from hardware
   ((0.0, 60.0, 0.0, 30.0, 0.0, 0.0),
    {'alpha': -0.0,
     'beta': 0.0,
     'naz': 0.0,
     'psi': 90.0,
     'qaz': 90.0,
     'tau': 90.0,
     'theta': 30.0}
    )
