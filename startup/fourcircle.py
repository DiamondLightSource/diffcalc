from startup._common_imports import *
import startup._demo

### Create dummy scannables ###
delta = Dummy('delta')
eta = Dummy('eta')
chi = Dummy('chi')
phi = Dummy('phi')
_fourc = ScannableGroup('_fourc', (delta, eta, chi, phi))
en = Dummy('en')
en.level = 3


### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_fourc, en, ESMTGKeV)
settings.geometry = diffcalc.hkl.you.geometry.FourCircle()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group= _fourc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())

# Load the last ub calculation used
lastub() 

demo = startup._demo.Demo(globals(), 'fourc')