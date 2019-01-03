from diffcalc.util import x_rotation, y_rotation, z_rotation, TORAD, TODEG
from startup._common_imports import *
from diffcalc.hkl.you.geometry import YouGeometry, YouPosition

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

if not GDA:
    import startup._demo


class FiveCircleI13(YouGeometry):
    """For a diffractometer with angles:
          delta, gamma, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'diffcalc_fivec', {'mu': 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta_phys, gam_phys, eta_phys, chi_phys, phi_phys = physical_angle_tuple
        return YouPosition(0, delta_phys, gam_phys, -eta_phys, -chi_phys, -phi_phys, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        _, delta_phys, gam_phys, eta_phys, chi_phys, phi_phys = clone_position.totuple()
        return delta_phys, gam_phys, -eta_phys, -chi_phys, -phi_phys


if '_fivec' in globals() and 'en' in globals():
    # Assume we are running in a live GDA deployment with a _fivec ScannableGroup
    # with axes named: delta, gam, eta, chi, phi.
    # Ensure that these five Scannables exist.
    # There must also be Scannable en for moving and reading the energy
    print "Diffcalc using predefined _fivec and en Scannables"
else:
    ### Create dummy scannables ###
    print "Diffcalc creating dummy Scannables as _fivec and en were not found"
    delta = Dummy('delta')
    gam = Dummy('gam')
    eta = Dummy('eta')
    chi = Dummy('chi')
    phi = Dummy('phi')
    _fivec = ScannableGroup('_fivec', (delta, gam, eta, chi, phi))
    en = Dummy('en')
    en.level = 3


### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_fivec, en, ESMTGKeV)
beamline_axes_transform = matrix([[0, 0, 1],[1, 0, 0], [0, 1, 0,]])
settings.geometry = FiveCircleI13(beamline_axes_transform=beamline_axes_transform)
settings.energy_scannable = en
settings.axes_scannable_group = _fivec
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV


from diffcalc.gdasupport.you import *  # @UnusedWildImport


if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
  
# Load the last ub calculation used  
# lastub()

# 
# setmax(delta, 28)
# setmin(delta, -1)
# setmin(gam, 0)
# setmax(gam, 16)
# setmin(eta, -10)
# setmax(eta, 10)
# setmin(chi, 90 - 12)
# setmax(chi, 90 + 12)
# setmin(phi, -88)
# setmax(phi, 88)
# setcut(phi, -90)
# hardware()

if not GDA:
    setmax(delta, 90)
    setmin(delta, -1)
    setmin(gam, 0)
    setmax(gam, 90)
    setmin(eta, -90)
    setmax(eta, 90)
    setmin(chi, -10)
    setmax(chi, 100)
    setmin(phi, -88)
    setmax(phi, 88)
    setcut(phi, -90)
hardware()



#def X(th_deg):
#    return x_rotation(th_deg * TORAD)
#
#
#def Y(th_deg):
#    return y_rotation(th_deg * TORAD)
#                      
#
#def Z(th_deg):
#    return z_rotation(th_deg * TORAD)
#
#
#WEDGE = X(15)


if not GDA:
    demo = startup._demo.Demo(globals(), 'fivec')
    
    
"""
Fivec, no real limits, working out U matrix
===========================================
U = xyz_rotation([-0.70711, 0.70711, 0.00000], 54.73561 * TORAD)
setu U
pos en 20
con qaz 90
con a_eq_b
UBCALC

   name:     2017-03-07-i13

   n_phi:     -0.00000  -0.00000   1.00000
   n_hkl:      0.57735   0.57735   0.57735 <- set
   miscut:
      angle:   0.00003
      axis:    0.70711  -0.70711   0.00000

CRYSTAL

   name:         Si111

   a, b, c:    5.43000   5.43000   5.43000
              90.00000  90.00000  90.00000

   B matrix:   1.15712   0.00000   0.00000
               0.00000   1.15712   0.00000
               0.00000   0.00000   1.15712

UB MATRIX

   U matrix:   0.78868  -0.21133  -0.57735
              -0.21132   0.78867  -0.57735
               0.57735   0.57735   0.57735

      angle:  54.73564
       axis:   0.70711  -0.70711   0.00000

   UB matrix:  0.91260  -0.24453  -0.66807
              -0.24453   0.91259  -0.66807
               0.66807   0.66807   0.66807

REFLECTIONS

     ENERGY     H     K     L     DELTA      GAM      ETA      CHI      PHI  TAG
   1 20.000  1.00  1.00  1.00   11.3483   0.0000   5.6741  90.0000  45.0000  
   2 20.000  4.00  0.00  0.00   26.3978   0.0000  13.1989  35.2644 -15.0000  

In [80]: listub
UB calculations in: /Users/zrb13439/.diffcalc/i13

 0) 2017-03-07-i13  14 Mar 2017 (14:35)
 1) test            07 Mar 2017 (11:38)
 
 In [81]: hardware
    -1.0 <= delta <=   90.0 (cut: -180.0)
     0.0 <=   gam <=   90.0 (cut: -180.0)
   -90.0 <=   eta <=   90.0 (cut: -180.0)
   -10.0 <=   chi <=  100.0 (cut: -180.0)
  -180.0 <=   phi <=  180.0 (cut:  -90.0)
Note: When auto sector/transforms are used,
       cuts are applied before checking limits.
       
Add in delta and gamma constraintss:
In [85]: atan(28/16)*TODEG
Out[85]: 45.0

In [86]: atan(28/16.)*TODEG
Out[86]: 60.25511870305777

In [87]: con qaz 60
    qaz  : 60.0000
    a_eq_b
    mu   : 0.0000

In [88]: sim hkl [4 0 0]
_fivec would move to:
  delta :   22.6459
    gam :   13.9379
    eta :   59.2132
    chi :    8.8270
    phi :  -63.0717

  alpha :    7.5752
   beta :    7.5752
    naz :    4.5446
    psi :   90.0000
    qaz :   60.0000
    tau :   54.7356
  theta :   13.1989

"""
