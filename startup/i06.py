from startup._common_imports import *  # @UnusedWildImport
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase  # @UnusedImport

from diffcalc.hkl.you.geometry import YouGeometry, YouPosition
from diffcalc.settings import NUNAME
from diffcalc.hardware import setrange
from diffcalc.hkl.you.calc import SMALL
if not GDA:    
    import startup._demo
else:
#     import __main__  # @UnresolvedImport
    from __main__ import dd2th,ddth,dummychi,energy  # @UnresolvedImport
LOCAL_MANUAL = "http://confluence.diamond.ac.uk/pages/viewpage.action?pageId=31853413"
# Diffcalc i06-1
# ======== === 
# delta    dd2th
# eta      ddth
# chi      dummy
# phi      0

class ThreeCircleI06(YouGeometry):
    """For a diffractometer with theta two-theta geometry:
          delta, eta
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'threec', {'mu': 0, NUNAME: 0, 'phi': 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta_phys, eta_phys, chi_phys = physical_angle_tuple
        return YouPosition(0, delta_phys, 0, eta_phys, chi_phys, 0, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        _, delta_phys, _, eta_phys, chi_phys, _ = clone_position.totuple()
        return delta_phys, eta_phys, chi_phys


### Create dummy scannables ###
if GDA:  
    print "!!! Starting LIVE diffcalc with delta(dd2th), eta(ddth), chi(dummy) and denergy." 
    _threec = ScannableGroup('_threec', (dd2th, ddth, dummychi))
    delta = _threec.dd2th
    eta = _threec.ddth
    en=energy
#     if float(en.getPosition()) == 0: # no energy value - dummy mode
#         en(800)
    
else:   
    delta = Dummy('delta')
    eta = Dummy('eta')
    chi = Dummy('chi')
    _threec = ScannableGroup('_threec', (delta, eta, chi))
    en = Dummy('en')
    en(800)
    
en.level = 3
 
### Configure and import diffcalc objects ###
ESMTGKeV = 0.001
settings.hardware = ScannableHardwareAdapter(_threec, en, ESMTGKeV)
settings.geometry = ThreeCircleI06()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group= _threec
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

if not GDA:
    setrange('chi', 90 - SMALL, 90 + SMALL)

from diffcalc.gdasupport.you import *  # @UnusedWildImport
 
if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
# Load the last ub calculation used
lastub() 
