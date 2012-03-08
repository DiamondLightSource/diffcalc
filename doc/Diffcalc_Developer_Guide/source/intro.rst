Introduction
============

Diffcalc is a diffraction condition calculator used for controlling
diffractometers within reciprocal lattice space. It is based on the papers
given in the :doc:`references <../references>` 



The core code will run by itself. However it makes more sense to use it
within Diamond's Gda framework which provides motor control, a scan mechanism
and more easily typed commands. An all-Python minimal framework, minigda, that
provides just the latter two of these features is provided within this distribution.

Diffcalc is written in Python. It will run under either Python 2.2 or
greater with the numpy module, or under Jython 2.2 with Java's Jama
matrix package.