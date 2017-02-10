# This file differs from dcyou in only two places

from diffcalc import settings
from diffcalc.dc.common import energy_to_wavelength
from diffcalc.dc.help import compile_extra_motion_commands_for_help
import diffcalc.hkl.willmott.calc


# reload to aid testing only
from diffcalc.ub import ub as _ub
reload(_ub)
from diffcalc import hardware as _hardware
#reload(_hardware)
from diffcalc.hkl.you import hkl as _hkl
reload(_hkl)

from diffcalc.ub.ub import *  # @UnusedWildImport
from diffcalc.hardware import *  # @UnusedWildImport
from diffcalc.hkl.willmot.hkl import *  # @UnusedWildImport
from diffcalc.gdasupport.scannable.sim import sim

def hkl_to_angles(h, k, l, energy=None):
    """Convert a given hkl vector to a set of diffractometer angles"""
    if energy is None:
        energy = settings.hardware.get_energy()  # @UndefinedVariable

    (pos, params) = hklcalc.hklToAngles(h, k, l, energy_to_wavelength(energy))
    angle_tuple = settings.geometry.internal_position_to_physical_angles(pos)  # @UndefinedVariable
    angle_tuple = settings.hardware.cut_angles(angle_tuple)  # @UndefinedVariable

    return angle_tuple, params

def angles_to_hkl(angleTuple, energy=None):
    """Converts a set of diffractometer angles to an hkl position
    ((h, k, l), paramDict)=angles_to_hkl(self, (a1, a2,aN), energy=None)"""
    if energy is None:
        energy = settings.hardware.get_energy()  # @UndefinedVariable
    i_pos = settings.geometry.physical_angles_to_internal_position(angleTuple)  # @UndefinedVariable
    return hklcalc.anglesToHkl(i_pos, energy_to_wavelength(energy))

settings.ubcalc_strategy = diffcalc.hkl.willmott.calc.WillmottHorizontalUbCalcStrategy()
settings.angles_to_hkl_function = diffcalc.hkl.willmott.calc.angles_to_hkl    
        

ub_commands_for_help = _ub.commands_for_help

hkl_commands_for_help = _hkl.commands_for_help + _hardware.commands_for_help + compile_extra_motion_commands_for_help()
