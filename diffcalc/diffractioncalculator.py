import diffcalc.help  # @UnusedImport for flag

from diffcalc.hkl.vlieg.commands import VliegHklCommands
from diffcalc.mapper.commands import MapperCommands
from diffcalc.ub.calculation import UBCalculation
from diffcalc.hkl.vlieg.calcvlieg import VliegHklCalculator
from diffcalc.mapper.sector import VliegSectorSelector
from diffcalc.mapper.mapper import PositionMapper
from diffcalc.utils import DiffcalcException, allnum
from diffcalc.hkl.vlieg.ubcalcstrategy import VliegUbCalcStrategy
from diffcalc.hkl.willmott.calcwill_horizontal import \
    WillmottHorizontalUbCalcStrategy, \
    WillmottHorizontalCalculator
from diffcalc.hkl.willmott.commands import WillmottHklCommands
from diffcalc.hkl.willmott.constraints import WillmottConstraintManager
from diffcalc.help import create_command_decorator, ExternalCommand
from diffcalc.ub.commands import UbCommands


_unused_commands = []
command = create_command_decorator(_unused_commands)

AVAILABLE_ENGINES = ('vlieg', 'willmott')


class DummySectorSelector(object):

    def transformPosition(self, pos):
        return pos


def create_diffcalc_vlieg(geometry,
                          hardware,
                          raise_exceptions_for_all_errors=True,
                          ub_persister=None):

    return _create_diffcalc(
        'vlieg', geometry, hardware, raise_exceptions_for_all_errors,
        ub_persister)


def create_diffcalc_willmot(geometry,
                            hardware,
                            raise_exceptions_for_all_errors=True,
                            ub_persister=None):
    return _create_diffcalc(
        'willmott', geometry, hardware, raise_exceptions_for_all_errors,
        ub_persister)


def _create_diffcalc(engine_name,
                     geometry,
                     hardware,
                     raise_exceptions_for_all_errors,
                     ub_persister):

    diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = \
        raise_exceptions_for_all_errors

    if engine_name not in AVAILABLE_ENGINES:
        raise ValueError(engine_name + ' not supported')

    # UB calculator
    if engine_name == 'vlieg':
        ubcalc_strategy = VliegUbCalcStrategy()
    elif engine_name == 'willmott':
        ubcalc_strategy = WillmottHorizontalUbCalcStrategy()
    ubcalc = UBCalculation(hardware, geometry, ub_persister, ubcalc_strategy)
    ub_commands = UbCommands(hardware, geometry, ubcalc)

    # Hkl
    if engine_name == 'vlieg':
        hklcalc = VliegHklCalculator(ubcalc, geometry, hardware, True)
        hkl_commands = VliegHklCommands(hardware, geometry, hklcalc)
    elif engine_name == 'willmott':
        hklcalc = WillmottHorizontalCalculator(
            ubcalc, geometry, hardware, WillmottConstraintManager())
        hkl_commands = WillmottHklCommands(hardware, geometry, hklcalc)

    # Mapper
    if engine_name == 'vlieg':
        sector_selector = VliegSectorSelector()
    elif engine_name == 'willmott':
        sector_selector = DummySectorSelector()

    # TODO: Split out into hardware commands and sector_selector commands
    mapper = PositionMapper(geometry, hardware, sector_selector)
    mapper_commands = MapperCommands(geometry, hardware, mapper)

    dc = Diffcalc(geometry, hardware, mapper,
                  ub_commands, hkl_commands, mapper_commands)

    dc.ub.commands.append(dc.checkub)

    dc.hkl.commands.append('Mapper')
    dc.hkl.commands.extend(dc.mapper.commands)
    dc.hkl.commands.append('Motion')
    dc.hkl.commands.append(dc.sim)

    _hwname = hardware.getDiffHardwareName()
    _angles = ', '.join(hardware.getPhysicalAngleNames())

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

    return dc


class Diffcalc(object):

    def __init__(self, geometry, hardware, mapper,
                 ub_commands, hkl_commands, mapper_commands):

        self._geometry = geometry
        self._hardware = hardware
        self._mapper = mapper

        self.ub = ub_commands
        self.hkl = hkl_commands
        self.mapper = mapper_commands

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

        (pos_unmapped, params) = self._hklcalc.hklToAngles(h, k, l, wavelength)
        pos = self._mapper.map(pos_unmapped)

        return pos, params

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

        intpos = self._geometry.physicalAnglesToInternalPosition(angleTuple)
        return self._hklcalc.anglesToHkl(intpos, wavelength)

    # This command requires the ubcalc
    @command
    def checkub(self):
        """checkub -- show calculated and entered hkl values for reflections.
        """

        s = "   %-6s %-4s %-4s %-4s  %-6s %-6s %-6s  tag\n" % \
        ('energy', 'h', 'k', 'l', 'h_comp', 'k_comp', 'l_comp')

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
                s += ("%-2d %-6.4f %-4.2f %-4.2f %-4.2f  %-6.4f %-6.4f %-6.4f"
                      "  %-s\n" % (n + 1, energy, hklguess[0], hklguess[1],
                      hklguess[2], hkl[0], hkl[1], hkl[2], tag))
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
            if diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS:
                raise TypeError(
                    "The first argument does not support simulated moves")
            else:
                print "The first argument does not support simulated moves"
