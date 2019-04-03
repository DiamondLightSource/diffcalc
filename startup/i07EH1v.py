from startup._common_imports import *  # @UnusedWildImport
from diffcalc.settings import NUNAME

if GDA:    
    from __main__ import diff1vdelta, diff1valpha, diff1vgamma, diff1vomega, dcm1energy # @UnresolvedImport

from diffcalc.hkl.you.geometry import YouGeometry, YouPosition


class FourCircleI07EH1v(YouGeometry):
    """For a diffractometer with angles:
          delta, gam, mu, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'fourc', {'eta': 0, 'chi': 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        delta_phys, gam_phys, mu_phys, phi_phys = physical_angle_tuple
        return YouPosition(mu_phys, delta_phys, gam_phys, 0, 0, phi_phys, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        mu_phys, delta_phys, gam_phys, _, _, phi_phys = clone_position.totuple()
        return delta_phys, gam_phys, mu_phys, phi_phys


### Create dummy scannables ###
if GDA:  
    ###map GDA scannable to diffcalc axis name###
    _fourc = ScannableGroup('_fourc', (diff1vdelta, diff1vgamma, diff1valpha, diff1vomega))
    delta=_fourc.diff1vdelta
    gam=_fourc.diff1vgamma
    mu=_fourc.diff1valpha
    phi=_fourc.diff1vomega
    en=dcm1energy
else:
    #Create dummy axes to run outside GDA in IPython#   
    delta = Dummy('delta')
    gam = Dummy(NUNAME)
    mu = Dummy('mu')
    phi = Dummy('phi')
    _fourc = ScannableGroup('_fourc', (delta, gam, mu, phi))
    en = Dummy('en')

en.level = 3

### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_fourc, en, ESMTGKeV)
settings.geometry = FourCircleI07EH1v()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group= _fourc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV
settings.include_reference = False

# for aliasing completeness
eta= settings.geometry.fixed_constraints['eta']
chi= settings.geometry.fixed_constraints['chi']
from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
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
    setmin(gam, -11.0)
    setmax(gam, 49.934) 
    setmin(mu, -6.561)
    setmax(mu, 29.163)
    setcut(phi, -180.0)
    print "Current hardware limits set to:"
    hardware()

if not GDA:
    setLimitsAndCuts()

# TODO: make demo code for (2+2) diffractometer geometry
#if not GDA:
#    demo = startup._demo.Demo(globals(), 'fourc')
