import diffcalc.help
from diffcalc.help import HelpList, UsageHandler
from diffcalc.hkl.common import sim, getNameFromScannableOrString

_hklcalcCommandHelp = HelpList()


class HklCommand(UsageHandler):
    def appendDocLine(self, line):
        _hklcalcCommandHelp.append(line)


class WillmottHklCommands(object):

    def __init__(self, hardware, geometry, hklcalc):
        self._hardware = hardware
        self._geometry = geometry
        self._hklcalc = hklcalc

        self._addDynamicHelpLines()

    def _addDynamicHelpLines(self):
        _hwname = self._hardware.getDiffHardwareName()
        _angles = ', '.join(self._hardware.getPhysicalAngleNames())
        _hklcalcCommandHelp.append(
            'pos %(_hwname)s %(_angles)s  -- move diffractometer to Eularian '
            'position. Use None to hold a value still' % vars())
        _hklcalcCommandHelp.append(
            'sim %(_hwname)s %(_angles)s -- simulate moving %(_hwname)s' %
             vars())
        _hklcalcCommandHelp.append(
            '%(_hwnames)-- info about current %(_hwname)s position' % vars())

    def __str__(self):
        return self._hklcalc.__str__()

    _hklcalcCommandHelp.append('Diffcalc')

    @HklCommand
    def helphkl(self, name=None):
        """helphkl [command] -- show help for one or all hkl commands
        """
        if name is None:
            print _hklcalcCommandHelp.getCompleteCommandUsageList()
        else:
            print _hklcalcCommandHelp.getCommandUsageString(str(name))

    _hklcalcCommandHelp.append(
        'helpub [command] -- show help for one or all ub commands')

### Settings ###
    _hklcalcCommandHelp.append('Calculator')

    #TODO: Messy, inconsistant use of square brackets in usage strings.

    _hklcalcCommandHelp.append('hkl -- shows info about current hkl position')

    _hklcalcCommandHelp.append(
        'pos hkl [h k l] -- move diffractometer to hkl, or read hkl position. '
        'Use None to hold a value still')

    @HklCommand
    def sim(self, scn, hkl):
        """sim hkl [h k l] --simulates moving hkl
        """
        sim(scn, hkl, diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS)

    @HklCommand
    def con(self, scn_or_string):
        """con <constraint> -- constrains constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.constrain(name)
        print self._report_constraints()

    @HklCommand
    def uncon(self, scn_or_string):
        """uncon <constraint> -- unconstrains constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.unconstrain(name)
        print self._report_constraints()

    @HklCommand
    def cons(self):
        """cons -- list available constraints and values
        """
        print self._report_constraints()

    def _report_constraints(self):
        return (self._hklcalc.constraints._build_display_table() + '\n\n' +
               self._hklcalc.constraints._report_constraints())

    _hklcalcCommandHelp.append('pos <constraint> -- sets constraint value')
