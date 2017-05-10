Project Files & Directories
===========================

diffcalc
   The main source package.

test
   Diffcalcs unit-test package (use Nose_ to run them).

diffcmd
    A spec-like openGDA emulator.

numjy
   A *very* minimal implentation of numpy for jython. It supports only what
   Diffcalc needs.
   
doc
   The documentation is written in reStructuredText and can be compiled into
   html and pdf using Python's `Sphinx <http://sphinx.pocoo.org>`_. With Sphinx
   installed use ``make clean all`` from within the user and developer guide
   folders to build the documentation.

startup
   Starup scripts called by diffcmd or openGDA to startup diffcalc
 
model
   Vrml models of diffractometers and a hokey script for animating then and
   controlling them from diffcalc.

.. _Nose: http://readthedocs.org/docs/nose/en/latest/