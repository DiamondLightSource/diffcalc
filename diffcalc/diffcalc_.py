from __future__ import absolute_import
# NOTE: The underscore in this module is used because Jython 2.5.2 does
#       not properly honour absolute_import

import diffcalc.util  # @UnusedImport for flag

from diffcalc.hkl.vlieg.commands import VliegHklCommands
from diffcalc.ub.calculation import UBCalculation
from diffcalc.hkl.vlieg.calcvlieg import VliegHklCalculator
from diffcalc.util import DiffcalcException, allnum
from diffcalc.hkl.vlieg.calcvlieg import VliegUbCalcStrategy
from diffcalc.hkl.willmott.calcwill_horizontal import \
    WillmottHorizontalUbCalcStrategy, \
    WillmottHorizontalCalculator
from diffcalc.hkl.willmott.commands import WillmottHklCommands
from diffcalc.hkl.willmott.constraints import WillmottConstraintManager
from diffcalc.util import command, ExternalCommand
from diffcalc.ub.commands import UbCommands
from diffcalc.hardware import HardwareCommands
from diffcalc.hkl.vlieg.transform import VliegTransformSelector, \
    TransformCommands, VliegPositionTransformer
from diffcalc.hkl.you.calcyou import YouUbCalcStrategy, YouHklCalculator
from diffcalc.hkl.you.commands import YouHklCommands
from diffcalc.hkl.you.constraints import YouConstraintManager


AVAILABLE_ENGINES = ('vlieg', 'willmott', 'you')


class DummySolutionTransformer(object):

    def transformPosition(self, pos):
        return pos


def create_diffcalc(engine_name,
                    geometry,
                    hardware,
                    raise_exceptions_for_all_errors,
                    ub_persister=None):

    diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = \
        raise_exceptions_for_all_errors

    if engine_name not in AVAILABLE_ENGINES:
        raise ValueError(engine_name + ' not supported')

    # UB calculator
    strategy_classes = {'vlieg': VliegUbCalcStrategy,
                        'willmott': WillmottHorizontalUbCalcStrategy,
                        'you': YouUbCalcStrategy}
    ubcalc_strategy = strategy_classes[engine_name]()
    ubcalc = UBCalculation(hardware, geometry, ub_persister, ubcalc_strategy)
    ub_commands = UbCommands(hardware, geometry, ubcalc)

    # Hkl
    if engine_name == 'vlieg':
        hklcalc = VliegHklCalculator(ubcalc, geometry, hardware, True)
        hkl_commands = VliegHklCommands(hklcalc, geometry)
    elif engine_name == 'willmott':
        hklcalc = WillmottHorizontalCalculator(
            ubcalc, geometry, hardware, WillmottConstraintManager())
        hkl_commands = WillmottHklCommands(hklcalc)
    elif engine_name == 'you':
        hklcalc = YouHklCalculator(
            ubcalc, geometry, hardware, YouConstraintManager(hardware))
        hkl_commands = YouHklCommands(hklcalc)

    # Hardware
    hardware_commands = HardwareCommands(hardware)

    # Mapper
    if engine_name == 'vlieg':
        transform_selector = VliegTransformSelector()
        transform_commands = TransformCommands(transform_selector)
        transformer = VliegPositionTransformer(geometry, hardware,
                                               transform_selector)
    else:
        transform_commands = None
        transformer = None

    dc = Diffcalc(geometry, hardware, transformer,
                  ub_commands, hkl_commands, hardware_commands,
                  transform_commands)

    _hwname = hardware.getDiffHardwareName()
    _angles = ', '.join(hardware.getPhysicalAngleNames())

    dc.ub.commands.append(dc.checkub)

    dc.hkl.commands.extend(dc.hardware.commands)

    if transform_commands is not None:
        dc.hkl.commands.extend(dc.transform.commands)

    dc.hkl.commands.append('Motion')
    dc.hkl.commands.append(dc.sim)
    dc.hkl.commands.append(ExternalCommand(
        '%(_hwname)s -- show Eularian position'))
    dc.hkl.commands.append(ExternalCommand(
        'pos %(_hwname)s [%(_angles)s]  -- move to Eularian position'
        '(None holds an axis still)' % vars()))
    dc.hkl.commands.append(ExternalCommand(
        'sim %(_hwname)s [%(_angles)s] -- simulate move to Eulerian position'
        '%(_hwname)s' % vars()))

    dc.hkl.commands.append(ExternalCommand(
        'hkl -- show hkl position'))
    dc.hkl.commands.append(ExternalCommand(
        'pos hkl [h k l] -- move to hkl position'))
    dc.hkl.commands.append(ExternalCommand(
        'pos <h|k|l> val -- move h, k or l to val'))
    dc.hkl.commands.append(ExternalCommand(
        'sim hkl [h k l] -- simulate move to hkl position'))

    if engine_name != 'vlieg':
        pass
        # TODO: remove sigtau command and 'Surface' string
    return dc


class Diffcalc(object):

    def __init__(self, geometry, hardware, transformer,
                 ub_commands, hkl_commands, hardware_commands,
                transform_commands):

        self._geometry = geometry
        self._hardware = hardware
        self._transformer = transformer

        self.ub = ub_commands
        self.hkl = hkl_commands
        self.hardware = hardware_commands
        if transform_commands is not None:
            self.transform = transform_commands

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.ub.__str__() + "\n" + self.hkl.__str__()

### Used by diffcalc scannables

    @property
    def parameter_manager(self):
        return self.hkl._hklcalc.parameter_manager

    @property
    def _ubcalc(self):
        return self.ub._ubcalc

    @property
    def _hklcalc(self):
        return self.hkl._hklcalc

    def hkl_to_angles(self, h, k, l, energy=None):
        """Convert a given hkl vector to a set of diffractometer angles"""
        if energy is None:
            energy = self._hardware.getEnergy()

        try:
            wavelength = 12.39842 / energy
        except ZeroDivisionError:
            raise DiffcalcException(
                "Cannot calculate hkl position as Energy is set to 0")

        (pos, params) = self._hklcalc.hklToAngles(h, k, l, wavelength)
        if self._transformer:
            pos = self._transformer.transform(pos)
        angle_tuple = self._geometry.internal_position_to_physical_angles(pos)
        angle_tuple = self._hardware.cutAngles(angle_tuple)

        return angle_tuple, params

    def angles_to_hkl(self, angleTuple, energy=None):
        """Converts a set of diffractometer angles to an hkl position
        ((h, k, l), paramDict)=angles_to_hkl(self, (a1, a2,aN), energy=None)"""
        #we will assume this is called correctly, as it is not a user command
        if energy is None:
            energy = self._hardware.getEnergy()

        try:
            wavelength = 12.39842 / energy
        except ZeroDivisionError:
            raise DiffcalcException(
                "Cannot calculate hkl position as Energy is set to 0")

        i_pos = self._geometry.physical_angles_to_internal_position(angleTuple)
        return self._hklcalc.anglesToHkl(i_pos, wavelength)

    # This command requires the ubcalc
    @command
    def checkub(self):
        """checkub -- show calculated and entered hkl values for reflections.
        """

        s = "\n   %7s  %4s  %4s  %4s   %6s  %6s  %6s   TAG\n" % \
        ('ENERGY', 'H', 'K', 'L', 'H_COMP', 'K_COMP', 'L_COMP')

        if self._ubcalc.getReflist() is None:
            s += "<<empty>>"
        else:
            reflist = self._ubcalc.getReflist()
            if len(reflist) == 0:
                s += "<<empty>>"
            for n in range(len(reflist)):
                hklguess, pos, energy, tag, time = reflist.getReflection(n + 1)
                wavelength = 12.39842 / energy
                hkl, params = self._hklcalc.anglesToHkl(pos, wavelength)
                del time, params
                if tag is None:
                    tag = ""
                s += ("%-2d %-6.4f  %-4.2f  %-4.2f  %-4.2f   %-6.4f  %-6.4f  "
                      "%-6.4f   %-s\n" % (n + 1, energy, hklguess[0],
                      hklguess[1], hklguess[2], hkl[0], hkl[1], hkl[2], tag))
        print s

    @command
    def sim(self, scn, hkl):
        """sim hkl scn -- simulates moving scannable (not all)
        """
        if not isinstance(hkl, (tuple, list)):
            raise TypeError

        if not allnum(hkl):
            raise TypeError()

        try:
            print scn.simulateMoveTo(hkl)
        except AttributeError:
            if diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS:
                raise TypeError(
                    "The first argument does not support simulated moves")
            else:
                print "The first argument does not support simulated moves"
