from startup._common_imports import *

### Create dummy scannables ###
print "Dummy scannables: sixc(mu, delta, gam, eta, chi, phi) and en"
mu = Dummy('mu')
delta = Dummy('delta')
gam = Dummy('gam')
eta = Dummy('eta')
chi = Dummy('chi')
phi = Dummy('phi')
_sixc = ScannableGroup('_sixc', (mu, delta, gam, eta, chi, phi))
en = Dummy('en')
en.level = 3


### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_sixc, en, ESMTGKeV)
settings.geometry = diffcalc.hkl.you.geometry.SixCircle()
settings.energy_scannable = en
settings.axes_scannable_group= _sixc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
    
lastub()  # Load the last ub calculation used



# iPython removes the actual command from namespace
diffcalc.hardware.setrange(chi, -2, 100)
diffcalc.hardware.setrange(eta, -2, 92)
diffcalc.hardware.setrange(delta, -2, 145)
diffcalc.hardware.setrange(gam, -2, 145)
diffcalc.hardware.hardware()

