from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.hkloffset import HklOffset
from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
from diffcalc.gdasupport.scannable.wavelength import Wavelength
from diffcalc.gdasupport.scannable.parameter import DiffractionCalculatorParameter


from diffcalc.dc import dcyou as _dc
from diffcalc.dc.help import format_command_help
from diffcalc.gdasupport.scannable.sr2 import Sr2
reload(_dc)
from diffcalc.dc.dcyou import *  # @UnusedWildImport
from diffcalc import settings

try:
    import gda  # @UnusedImport @UnresolvedImport
    GDA = True
except:
    GDA = False
    
if not GDA:
    from diffcalc.gdasupport.minigda import command
    _pos = command.Pos()
    _scan = command.Scan(command.ScanDataPrinter())

    def pos(*args):
        """
        pos                   show position of all Scannables
        pos scn               show position of scn
        pos scn targetmove    scn to target (a number)
        """
        return _pos(*args)

    def scan(*args):
        """
        scan scn start stop step {scn {target}} {det t}
        """
        return _scan(*args)


from diffcalc.gdasupport.scannable.sim import sim  # @UnusedImport

_scn_group = settings.axes_scannable_group
_diff_scn_name = settings.geometry.name # @UndefinedVariable
_energy_scannable = settings.energy_scannable


# Create diffractometer scannable
_diff_scn = DiffractometerScannableGroup(_diff_scn_name, _dc, _scn_group)
globals()[_diff_scn_name] = _diff_scn

# Create hkl scannables
hkl = Hkl('hkl', _scn_group, _dc)
h = hkl.h
k = hkl.k
l = hkl.l

hkloffset = HklOffset('hkloffset', _scn_group, _dc)
h_offset = hkloffset.h
k_offset = hkloffset.k
l_offset = hkloffset.l
pol_offset = hkloffset.polar
az_offset = hkloffset.azimuthal

sr2 = Sr2('sr2', _scn_group, _dc)

Hkl.dynamic_docstring = format_command_help(hkl_commands_for_help)  # must be on the class
ub.__doc__ = format_command_help(ub_commands_for_help)

_virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta', 'bin', 'bout')
hklverbose = Hkl('hklverbose', _scn_group, _dc, _virtual_angles)


# Create wavelength scannable
wl = Wavelength(
    'wl', _energy_scannable, settings.energy_scannable_multiplier_to_get_KeV)
if not GDA:
    wl.asynchronousMoveTo(1)  # Angstrom
_energy_scannable.level = 3
wl.level = 3


# Create simulated counter timer
ct = SimulatedCrystalCounter('ct', _scn_group, settings.geometry, wl)
ct.level = 10


# Create constraint scannables
def _create_constraint_scannable(con_name, scn_name=None):
    if not scn_name:
        scn_name = con_name
    return DiffractionCalculatorParameter(
        scn_name, con_name, _dc.constraint_manager)
     
# Detector constraints
def isconstrainable(name):
    return not constraint_manager.is_constraint_fixed(name)

if isconstrainable('delta'): delta_con = _create_constraint_scannable('delta', 'delta_con')
if isconstrainable('gam'): gam_con = _create_constraint_scannable('gam', 'gam_con')
if isconstrainable('qaz'): qaz = _create_constraint_scannable('qaz')
if isconstrainable('naz'): naz = _create_constraint_scannable('naz')

# Reference constraints
alpha = _create_constraint_scannable('alpha')
beta = _create_constraint_scannable('beta')
psi = _create_constraint_scannable('psi')
a_eq_b = 'a_eq_b'

# Sample constraints
if isconstrainable('mu'): mu_con = _create_constraint_scannable('mu', 'mu_con')
if isconstrainable('eta'): eta_con = _create_constraint_scannable('eta', 'eta_con')
if isconstrainable('chi'): chi_con = _create_constraint_scannable('chi', 'chi_con')
if isconstrainable('phi'): phi_con = _create_constraint_scannable('phi', 'phi_con')
if isconstrainable('mu') and isconstrainable('gam'): mu_is_gam = 'mu_is_gam'
omega = _create_constraint_scannable('omega')
bisect = 'bisect'


# Cleanup other cruft
del format_command_help
