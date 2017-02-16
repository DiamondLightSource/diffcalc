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
    print "Dummy scannables: _fivec(delta, gam, eta, chi, phi) and en"
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
    
lastub()  # Load the last ub calculation used
