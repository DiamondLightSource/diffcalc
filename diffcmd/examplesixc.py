from __future__ import absolute_import
import diffcalc.diffcalc_

from diffcalc.gdasupport.scannable.diffractometer import DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.parameter import DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter
from diffcalc.gdasupport.scannable.wavelength import Wavelength
from diffcalc.hardware import ScannableHardwareAdapter
from diffcalc.ub.persistence import UBCalculationJSONPersister

import diffcalc.hkl.you.geometry
import diffcalc.util # @UnusedImport for flag
import os

from diffcalc.gdasupport.minigda.scannable import SingleFieldDummyScannable,\
    ScannableGroup
import diffcalc.gdasupport.minigda.command

from IPython.core.magic import register_line_magic
from diffcmd.ipython import parse_line

    
GLOBAL_NAMESPACE_DICT = {}


#_demo = []
#_demo.append("pos wl 1")
#_demo.append("en")
#_demo.append("newub 'test'")
#_demo.append("setlat 'cubic' 1 1 1 90 90 90")
#_demo.append("c2th [1 0 0]")
#_demo.append("pos sixc [0 60 0 30 0 0]")
#_demo.append("addref 1 0 0 'ref1'")
#_demo.append("c2th [0 1 0]")
#_demo.append("pos phi 90")
#_demo.append("addref 0 1 0 'ref2'")
#_demo.append("checkub")

############ Define diffractometer and other hardware here ####################

# Create axes
mu = SingleFieldDummyScannable('mu')
delta = SingleFieldDummyScannable('delta')
gam = SingleFieldDummyScannable('gam')
eta = SingleFieldDummyScannable('eta')
chi = SingleFieldDummyScannable('chi')
phi = SingleFieldDummyScannable('phi')
sixc_group = ScannableGroup('sixc', [mu, delta, gam, eta, chi, phi])

# Create wavelength and energy
en = SingleFieldDummyScannable('en')  # keV
wl = Wavelength('wl', en, energyScannableMultiplierToGetKeV=1)
wl.asynchronousMoveTo(1)  # Angstrom
en.level = 3
wl.level =3

# Create hardware adapter
_hardware = ScannableHardwareAdapter(
    sixc_group, en, energyScannableMultiplierToGetKeV=1)

# Define the geometry
_geometry = diffcalc.hkl.you.geometry.SixCircle()

###############################################################################
_ub_persister = UBCalculationJSONPersister(os.getcwd())
_dc = diffcalc.diffcalc_.create_diffcalc('you', _geometry, _hardware, _ub_persister)



#######

sixc = DiffractometerScannableGroup('sixc', _dc, sixc_group)

hkl = Hkl('hkl', sixc_group, _dc)
h = hkl.h
k = hkl.k
l = hkl.l

_virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
hklverbose = Hkl('hklverbose', sixc_group, _dc, _virtual_angles)

ct = SimulatedCrystalCounter('ct', sixc, _geometry, wl)
ct.level = 10

sixc_group

def _create_constraint_scannable(param_name, scn_name=None):
    if not scn_name:
        scn_name = param_name
    return DiffractionCalculatorParameter(scn_name, param_name, _dc.parameter_manager)
     
# Detector constraints                                
delta_con = _create_constraint_scannable('delta', 'delta_con')
gam_con = _create_constraint_scannable('gam', 'gam_con')
qaz = _create_constraint_scannable('qaz')
naz = _create_constraint_scannable('naz')

# Reference constraints
alpha = _create_constraint_scannable('alpha')
beta = _create_constraint_scannable('beta')
psi = _create_constraint_scannable('psi')
a_eq_b = 'a_eq_b'

# Sample constraints
mu_con = _create_constraint_scannable('mu', 'mu_con')
eta_con = _create_constraint_scannable('eta', 'eta_con')
chi_con = _create_constraint_scannable('chi', 'chi_con')
phi_con = _create_constraint_scannable('phi', 'phi_con')
mu_is_gam = 'mu_is_gam'

###############################################################################

pos = diffcalc.gdasupport.minigda.command.Pos(globals())
_data_handelr = diffcalc.gdasupport.minigda.command.ScanDataPrinter()
scan = diffcalc.gdasupport.minigda.command.Scan(_data_handelr)

###############################################################################

@register_line_magic
@parse_line
def check_parser(*args):
    return args


@register_line_magic
@parse_line
def newub(*args):
    return _dc.ub.commands.newub(args)

@register_line_magic
@parse_line
def pos(*args):
    return pos(args)

 
# newub,
# loadub,
# listub,
# saveubas,
# ub,
#                          'Lattice',
# setlat,
# c2th,
#                          'Surface',
# sigtau,
#                          'Reflections',
# showref,
# addref,
# editref,
# delref,
# swapref,
#                          'ub',
# setu,
# setub,
# calcub,
# trialub]



