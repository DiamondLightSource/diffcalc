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
should use the 'You' engine.

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

- **The User manual next to this developer manual or README file on github.**
- The :ref:`quickstart-api` section describes how to run up only
  the core in Python_. This provides a base option for system integration.

Diffcalc will work with Python 2.7 or higher with numpy_, or with
Jython 2.7 of higher with Jama_.


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
