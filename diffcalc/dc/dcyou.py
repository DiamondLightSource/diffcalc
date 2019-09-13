from diffcalc import settings
from diffcalc.dc.common import energy_to_wavelength
from diffcalc.dc.help import compile_extra_motion_commands_for_help

import diffcalc.hkl.you.calc
settings.ubcalc_strategy = diffcalc.hkl.you.calc.YouUbCalcStrategy()
settings.angles_to_hkl_function = diffcalc.hkl.you.calc.youAnglesToHkl

# reload to aid testing only
from diffcalc.ub import ub as _ub

reload(_ub)
from diffcalc import hardware as _hardware
#reload(_hardware)
from diffcalc.hkl.you import hkl as _hkl
reload(_hkl)

from diffcalc.ub.ub import *  # @UnusedWildImport
from diffcalc.hardware import *  # @UnusedWildImport
from diffcalc.hkl.you.hkl import *  # @UnusedWildImport


class DiffractometerYouCalculator(object):

    def __init__(self, diffractometerObject, diffcalcObject):
        self.diffhw = diffractometerObject
        self.geometry = diffcalcObject


    def hkl_to_angles(self, h, k, l, energy=None):
        """Convert a given hkl vector to a set of diffractometer angles
        
        return angle tuple and params dictionary
        
        """
        if energy is None:
            energy = self.diffhw.get_energy()  # @UndefinedVariable
    
        (pos, params) = hklcalc.hklToAngles(h, k, l, energy_to_wavelength(energy))
        angle_tuple = self.geometry.internal_position_to_physical_angles(pos)  # @UndefinedVariable
        angle_tuple = self.diffhw.cut_angles(angle_tuple)  # @UndefinedVariable
    
        return angle_tuple, params
    
    
    def hkl_list_to_angles(self, hkl_list, energy=None):
        """Convert a given hkl vector to a set of diffractometer angles
        
        return angle tuple and params dictionary
        
        """
        if energy is None:
            energy = self.diffhw.get_energy()  # @UndefinedVariable
    
        (pos, params) = hklcalc.hklListToAngles(hkl_list, energy_to_wavelength(energy))
        angle_tuple = self.geometry.internal_position_to_physical_angles(pos)  # @UndefinedVariable
        angle_tuple = self.diffhw.cut_angles(angle_tuple)  # @UndefinedVariable
    
        return angle_tuple, params
    
    
    def angles_to_hkl(self, angleTuple, energy=None):
        """Converts a set of diffractometer angles to an hkl position
        
        Return hkl tuple and params dictionary
        
        """
        if energy is None:
            energy = self.diffhw.get_energy()  # @UndefinedVariable
        i_pos = self.geometry.physical_angles_to_internal_position(angleTuple)  # @UndefinedVariable
        return hklcalc.anglesToHkl(i_pos, energy_to_wavelength(energy))


def hkl_to_angles(h, k, l, energy=None):
    _dcyou = DiffractometerYouCalculator(settings.hardware, settings.geometry)
    return _dcyou.hkl_to_angles(h, k, l, energy)

def hkl_list_to_angles(hkl, energy=None):
    _dcyou = DiffractometerYouCalculator(settings.hardware, settings.geometry)
    return _dcyou.hkl_list_to_angles(hkl, energy)

def angles_to_hkl(angleTuple, energy=None):
    _dcyou = DiffractometerYouCalculator(settings.hardware, settings.geometry)
    return _dcyou.angles_to_hkl(angleTuple, energy)



ub_commands_for_help = _ub.commands_for_help
hkl_commands_for_help = _hkl.commands_for_help + _hardware.commands_for_help + compile_extra_motion_commands_for_help()
