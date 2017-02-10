from diffcalc.dc.common import energy_to_wavelength

from diffcalc import settings
from diffcalc.hkl.vlieg.transform import VliegTransformSelector,\
    TransformCommands, VliegPositionTransformer
from diffcalc.dc.help import compile_extra_motion_commands_for_help
import diffcalc.hkl.vlieg.calc


# reload to aid testing only
import diffcalc.ub.ub as _ub
reload(_ub)
from diffcalc import hardware as _hardware
#reload(_hardware)
import diffcalc.hkl.vlieg.hkl as _hkl
reload(_hkl)

from diffcalc.ub.ub import *  # @UnusedWildImport
from diffcalc.hardware import *  # @UnusedWildImport
from diffcalc.hkl.vlieg.hkl import *  # @UnusedWildImport
from diffcalc.gdasupport.scannable.sim import sim

_transform_selector = VliegTransformSelector()
_transform_commands = TransformCommands(_transform_selector)
_transformer = VliegPositionTransformer(settings.geometry, settings.hardware,
                                       _transform_selector)

transform = _transform_commands.transform
transforma = _transform_commands.transforma
transformb = _transform_commands.transformb
transformc = _transform_commands.transformc


on = 'on'
off = 'off'
auto = 'auto'
manual = 'manual'
    
def hkl_to_angles(h, k, l, energy=None):
    """Convert a given hkl vector to a set of diffractometer angles"""
    if energy is None:
        energy = settings.hardware.get_energy()  # @UndefinedVariable

    position, params = hklcalc.hklToAngles(h, k, l, energy_to_wavelength(energy))
    position = _transformer.transform(position)
    angle_tuple = settings.geometry.internal_position_to_physical_angles(position)  # @UndefinedVariable
    angle_tuple = settings.hardware.cut_angles(angle_tuple)  # @UndefinedVariable
 
    return angle_tuple, params


def angles_to_hkl(angleTuple, energy=None):
    """Converts a set of diffractometer angles to an hkl position
    ((h, k, l), paramDict)=angles_to_hkl(self, (a1, a2,aN), energy=None)"""
    if energy is None:
        energy = settings.hardware.get_energy()  # @UndefinedVariable

    i_pos = settings.geometry.physical_angles_to_internal_position(angleTuple)  # @UndefinedVariable
    return hklcalc.anglesToHkl(i_pos, energy_to_wavelength(energy))


settings.ubcalc_strategy = diffcalc.hkl.vlieg.calc.VliegUbCalcStrategy()
settings.angles_to_hkl_function = diffcalc.hkl.vlieg.calc.vliegAnglesToHkl       
settings.include_sigtau = True

ub_commands_for_help = _ub.commands_for_help

hkl_commands_for_help = (_hkl.commands_for_help +
                         _hardware.commands_for_help +
                         ['Transform',
                          transform,
                          transforma,
                          transformb,
                          transformc] +
                          compile_extra_motion_commands_for_help())

