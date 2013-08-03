Introduction
============

Diffcalc is a diffraction condition calculator used for controlling
diffractometers within reciprocal lattice space. It performs the same
task as the ``fourc``, ``sixc``, ``twoc``, ``kappa``, ``psic`` and
``surf`` macros from SPEC_.

Diffcalc's standard calculation engine is an implementation of
[You1999]_ . The first versions of Diffcalc were based on
[Vlieg1993]_ and [Vlieg1998]_ and a 'Vlieg' engine is still
available. The 'You' engine is more generic and the plan is to remove
the old 'Vlieg' engine once beamlines have been migrated. New users
should use the 'You' engine. [*]_

The foundations for this type of calculation were laid by by Busing &
Levi in their classic paper [Busing1967]_. Diffcalc's orientation
algorithm is taken from this paper. Busing & Levi also provided the
original definition of the coordinate frames and of the U and B
matrices used to describe a crystal's orientation and to convert between
Cartesian and reciprical lattice space.

Geometry plugins are used to adapt the six circle model used
internally by Diffcalc to apply to other diffractometers. These
contain a dictionary of the 'missing' angles which Diffcalc uses to
constrain these angles internally, and a methods to map from external
angles to Diffcalc angles and visa versa.

Options to use Diffcalc:

- The :ref:`quickstart-api` section describes how to run up only
  the core in Python_ or IPython_. This provides a base option for
  system integration.
- The :ref:`quickstart-scan` section describes how to start Diffcalc
  in Python in a way that provides a scan command and that also
  exposes user-level commands to the root namespace. This does not
  provide motor control, but does provide dummy software motor objects
  that could be easily replaced with real implementations for EPICS or
  TANGO for example.
- The :ref:`quickstart-opengda` section describes how to start Diffcalc
  within the Jython interpreter of an OpenGDA_ server. OpenGDA
  provides a scan command, a system for controlling motors and also a
  way to 'alias' user-level commands so that brackets and commas need
  not be typed, e.g typing:
  
     >>> addref [1 0 0]
  
  calls from the root namespace::
  
     >>> addref([1, 0, 0])
     
Diffcalc will work with Python 2.5 or higher with numpy_, or with
Jython 2.5 of higher with Jama_.


.. [*] The very small 'Willmott' engine currently handles the case for
       surface diffraction where the surface normal is held vertical
       [Willmott2011]_.  The 'You' engine handles this case fine, but
       currently spins nu into an unhelpful quadrant. We hope to
       remove the need for this engine soon.


.. _SPEC: http://www.certif.com/
.. _Python: http://python.org
.. _IPython: http://http://ipython.org/
.. _Jython: http://jython.org
.. _OpenGDA: http://opengda.org
.. _numpy: http://numpy.scipy.org/
.. _Jama:  http://math.nist.gov/javanumerics/jama/


.. include:: ../../references
