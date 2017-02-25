from startup._common_imports import *


diffcalc.util.COLOURISE_TERMINAL_OUTPUT = False

### Create dummy scannables ###
print "Dummy scannables: sixc(mu, delta, gam, eta, chi, phi) and en"
mu = Dummy('mu')
delta = Dummy('delta')
gam = Dummy('gam')
eta = Dummy('eta')
chi = Dummy('chi')
phi = Dummy('phi')
_sixc = ScannableGroup('sixc', (mu, delta, gam, eta, chi, phi))
en = Dummy('en')
en.level = 3


### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_sixc, en, ESMTGKeV)
settings.geometry = diffcalc.hkl.you.geometry.SixCircle()  # @UndefinedVariable
settings.energy_scannable = en
settings.axes_scannable_group= _sixc
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV


# For manual!
from diffcalc.ub.persistence import UbCalculationNonPersister
settings.ubcalc_persister = UbCalculationNonPersister()

from diffcalc.gdasupport.you import *  # @UnusedWildImport


DIFFCALC_ROOT = os.sep.join(
    os.path.realpath(diffcalc.__file__).split(os.sep)[:-2])

MANUALS_TO_MAKE = [
    os.path.join(
        DIFFCALC_ROOT, 'doc', 'source', 'youmanual_template.rst'),
    os.path.join(
        DIFFCALC_ROOT, 'README_template.rst')]

print 'MANUALS_TO_MAKE: ', MANUALS_TO_MAKE
