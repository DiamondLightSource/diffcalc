Project Files & Directories
===========================

diffcalc
   The main source package.

test
   Diffcalcs unit-test package (use Nose_ to run them).

numjy
   A *very* minimal implentation of numpy for jython. It supports only what
   Diffcalc needs.
   
doc
   The documentation is written in reStructuredText and can be compiled into
   html and pdf using Python's `Sphinx <http://sphinx.pocoo.org>`_. With Sphinx
   installed use ``make clean all`` from within the user and developer guide
   folders to build the documentation.

doc/references
   Includes links to relevant papers.

example
   Example startup scripts.
 
model
   Vrml models of diffractometers and a hokey script for animating then and
   controlling them from diffcalc.

.. _Nose: http://readthedocs.org/docs/nose/en/latest/