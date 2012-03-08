Diffcalc's standard 'You' calculation engine is taken from this paper:

- H. You. *Angle calculations for a '4S+2D' six-circle diffractometer.*
  J. Appl. Cryst. (1999). 32, 614-623. `pdf
  <http://journals.iucr.org/j/issues/1999/04/00/hn0093/hn0093.pdf>`__.
  
This classic paper was the start of it all. It defines the coordinated system
used by Diffcalc, how the B matrix is derived from lattice parameters, and the
U matrix:

- W. R. Busing and H. A. Levy. *Angle calculations for 3- and 4-circle X-ray
  and neutron diffractometers.* Acta Cryst. (1967). 22, 457-464. `pdf
  <http://journals.iucr.org/q/issues/1967/04/00/a05492/a05492.pdf>`__.

The original 'Vlieg' calculation engine used by Diffcalc is taken from this
paper (new users should use the 'You' engine):

- Martin Lohmeier and Elias Vlieg. *Angle calculations for a six-circle
  surface x-ray diffractometer.* J. Appl. Cryst. (1993). 26, 706-716. `pdf
  <http://journals.iucr.org/j/issues/1993/05/00/la0044/la0044.pdf>`__.

The transformation between settings for the detectors described above and more
modern diffractometer geometries is given here:

- Elias Vlieg. *A (2+3)-type surface diffractometer: mergence of the z-axis and
  (2+2)-type geometries.* J. Appl. Cryst. (1998). 31, 198-203. `pdf
  <http://journals.iucr.org/j/issues/1998/02/00/pe0028/pe0028.pdf>`__. 

The very small 'Willmott' calculation engine handles the case for surface
diffraction where the surface normal is held vertical (The 'You' engine handles
this case fine, but currently spins nu into the wrong quadrant):

- C. M. Schlepütz, S. O. Mariager, S. A. Pauli, R. Feidenhans'l and
  P. R. Willmott. *Angle calculations for a (2+3)-type diffractometer: focus
  on area detectors.* J. Appl. Cryst. (2011). 44, 73-83. `pdf
  <http://journals.iucr.org/j/issues/2011/01/00/db5088/db5088.pdf>`__.
