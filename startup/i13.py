from diffcalc.util import x_rotation, y_rotation, z_rotation, TORAD
import startup._demo
from startup._common_imports import *


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
settings.geometry = diffcalc.hkl.you.geometry.FiveCircle()
settings.energy_scannable = en
settings.axes_scannable_group = _fivec
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV


from diffcalc.gdasupport.you import *  # @UnusedWildImport


if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
 
  
# Load the last ub calculation used  
lastub()


setmax(delta, 28)
setmin(delta, -1)
setmin(gam, 0)
setmax(gam, 16)
setmin(eta, -10)
setmax(eta, 10)
setmin(chi, 90 - 12)
setmax(chi, 90 + 12)
setmin(phi, -88)
setmax(phi, 88)
setcut(phi, -90)
hardware()



def X(th_deg):
    return x_rotation(th_deg * TORAD)


def Y(th_deg):
    return y_rotation(th_deg * TORAD)
                      

def Z(th_deg):
    return z_rotation(th_deg * TORAD)


WEDGE = X(15)


if not GDA:
    demo = startup._demo.Demo(globals(), 'fivec')