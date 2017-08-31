from startup._common_imports import *
import startup._demo

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
settings.geometry = diffcalc.hkl.you.geometry.FiveCircle()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group = _fivec
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
    
lastub()  # Load the last ub calculation used

# Set some limits
setmin('gam', -179)
setmax('gam', 179)

demo = startup._demo.Demo(globals(), 'fivec')