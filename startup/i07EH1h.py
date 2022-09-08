from startup._common_imports import *  # @UnusedWildImport
from diffcalc.settings import NUNAME

if GDA:    
    from __main__ import diff1delta, diff1chi, diff1gamma, diff1theta, dcm1energy # @UnresolvedImport

from diffcalc.hkl.you.geometry import YouRemappedGeometry

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix


class FourCircleI07EH1h(YouRemappedGeometry):
    """For a diffractometer with angles:
          delta, gam, eta, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouRemappedGeometry.__init__(self, 'fourc', {'mu': 0, 'chi': 90}, beamline_axes_transform)

        # Order should match scannable order in _fourc group for mapping to work correctly
        omega_to_phi = lambda x: 180. - x
        self._scn_mapping_to_int = (('delta', lambda x: x),
                                    ('gam',   lambda x: x),
                                    ('eta',   lambda x: x),
                                    ('phi',   omega_to_phi))
        phi_to_omega = lambda x: ((180. - x) + 180.) % 360 - 180
        self._scn_mapping_to_ext = (('delta', lambda x: x),
                                    ('gam',   lambda x: x),
                                    ('eta',   lambda x: x),
                                    ('phi',   phi_to_omega))

### Create dummy scannables ###
if GDA:  
    ###map GDA scannable to diffcalc axis name###
    _fourc = ScannableGroup('_fourc', (diff1delta, diff1gamma, diff1chi, diff1theta))
    delta=_fourc.diff1delta
    gamma=_fourc.diff1gamma
    chi=_fourc.diff1chi
    theta=_fourc.diff1theta
    alpha = diff1alpha
    omega = diff1omega
    en=dcm1energy
    if float(en.getPosition()) == 0: # no energy value - dummy mode
        en(800)
else:
    #Create dummy axes to run outside GDA in IPython#   
    delta = Dummy('delta')
    gamma = Dummy('gamma')
    chi = Dummy('chi')
    theta = Dummy('theta')
    alpha = Dummy('alpha')
    _fourc = ScannableGroup('_fourc', (delta, gamma, chi, theta))
    en = Dummy('en')
    en(800)

en.level = 3

### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_fourc, en, ESMTGKeV)
settings.geometry = FourCircleI07EH1h()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group= _fourc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
settings.include_reference = False
 
from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    omega = diff1omega
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
# Load the last ub calculation used
lastub()
# Set reference vector direction returning betain and betaout angles as alpha and beta
if ubcalc.name:
    surfnphi('0; 0; 1')

### Set i07 specific limits
def setLimitsAndCuts():
    ''' set motor limits for diffcalc, these are within the actual motor limits
    '''
    setmin(delta, -11.275)
    setmax(delta, 100.0) 
    setmin(gamma, -11.0)
    setmax(gamma, 49.934)
    setmin(chi, -5.096)
    setmax(chi,  5.115)
    setcut(omega, -180.0)
    print "Current hardware limits set to:"
    hardware()

if not GDA:
    setLimitsAndCuts()

# TODO: make demo code for (2+2) diffractometer geometry
#if not GDA:
#    demo = startup._demo.Demo(globals(), 'fourc')
