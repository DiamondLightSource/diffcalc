import diffcalc.help
from diffcalc.help import HelpList, UsageHandler
from diffcalc.hkl.common import sim, getNameFromScannableOrString

_hklcalcCommandHelp = HelpList()


class HklCommand(UsageHandler):

    def appendDocLine(self, line):
        _hklcalcCommandHelp.append(line)


class VliegHklCommands(object):

    def __init__(self, hardware, geometry, hklcalc):
        self._hardware = hardware
        self._geometry = geometry
        self._hklcalc = hklcalc

        self._addDynamicHelpLines()

    def _addDynamicHelpLines(self):
        angleNames = self._hardware.getPhysicalAngleNames()
        formatStr = ("[" + "%s, " * len(angleNames))[:-1] + "]"
        diffHwName = self._hardware.getDiffHardwareName()
        _hklcalcCommandHelp.append(
            'pos ' + diffHwName + ' ' + formatStr % angleNames + ' --move '
            'diffractometer to Eularian position. Use None to hold a value '
            'still')
        _hklcalcCommandHelp.append(
            'sim ' + diffHwName + ' ' + formatStr % angleNames + '-- simulates'
            ' moving ' + diffHwName)
        _hklcalcCommandHelp.append(
            diffHwName + '-- shows loads of info about current ' + diffHwName +
            ' position')

    def __str__(self):
        return self._hklcalc.__str__()

    _hklcalcCommandHelp.append('Diffcalc')

    @HklCommand
    def helphkl(self, name=None):
        """
        helphkl [command] -- show help for one or all hkl commands
        """
        if name is None:
            print _hklcalcCommandHelp.getCompleteCommandUsageList()
        else:
            print _hklcalcCommandHelp.getCommandUsageString(str(name))

    _hklcalcCommandHelp.append(
        'helpub [command] -- show help for one or all ub commands')

### Settings ###
    _hklcalcCommandHelp.append('Calculator')

    @HklCommand
    def hklmode(self, num=None):
        """hklmode [num] -- changes mode or shows current and available modes and all settings""" #@IgnorePep8

        if num is None:
            print self._hklcalc.__str__()
        else:
            self._hklcalc.mode_selector.setModeByIndex(int(num))
            pm = self._hklcalc.parameter_manager
            print (self._hklcalc.mode_selector.reportCurrentMode() + "\n" +
                   pm.reportParametersUsedInCurrentMode())

    def _setParameter(self, name, value):
        self._hklcalc.parameter_manager.setParameter(name, value)

    def _getParameter(self, name):
        return self._hklcalc.parameter_manager.getParameter(name)

    @HklCommand
    def setpar(self, scannable_or_string=None, val=None):
        """setpar [parameter_scannable [val]] -- sets or shows a parameter'
        setpar [parameter_name [val]] -- sets or shows a parameter'
        """

        if scannable_or_string is None:
            #show all
            parameterDict = self._hklcalc.parameter_manager.getParameterDict()
            names = parameterDict.keys()
            names.sort()
            for name in names:
                print self._representParameter(name)
        else:
            name = getNameFromScannableOrString(scannable_or_string)
            if val is None:
                self._representParameter(name)
            else:
                oldval = self._getParameter(name)
                self._setParameter(name, float(val))
                print self._representParameter(name, oldval, float(val))

    def _representParameter(self, name, oldval=None, newval=None):
        flags = ''
        if self._hklcalc.parameter_manager.isParameterTracked(name):
            flags += '(tracking hardware) '
        if self._geometry.isParameterFixed(name):
            flags += '(fixed by geometry) '
        pm = self._hklcalc.parameter_manager
        if not pm.isParameterUsedInSelectedMode(name):
            flags += '(not relevant in this mode) '
        if oldval is None:
            val = self._getParameter(name)
            if val is None:
                val = "---"
            else:
                val = str(val)
            return "%s: %s %s" % (name, val, flags)
        else:
            return "%s: %s --> %f %s" % (name, oldval, newval, flags)

    def __checkInputAndSetOrShowParameterTracking(self, name, b=None):
        """
        for track-parameter commands: If no args displays parameter settings,
        otherwise sets the tracking switch for the given parameter and displays
        settings.
        """
        # set if arg given
        if b is not None:
            self._hklcalc.parameter_manager.setTrackParameter(name, b)
        # Display:
        lastValue = self._getParameter(name)
        if lastValue is None:
            lastValue = "---"
        else:
            lastValue = str(lastValue)
        flags = ''
        if self._hklcalc.parameter_manager.isParameterTracked(name):
            flags += '(tracking hardware)'
        print "%s: %s %s" % (name, lastValue, flags)

    @HklCommand
    def trackalpha(self, b=None):
        """trackalpha [boolean] -- determines wether alpha parameter will track alpha axis""" #@IgnorePep8
        self.__checkInputAndSetOrShowParameterTracking('alpha', b)

    @HklCommand
    def trackgamma(self, b=None):
        """trackgamma [boolean] -- determines wether gamma parameter will track alpha axis""" #@IgnorePep8
        self.__checkInputAndSetOrShowParameterTracking('gamma', b)

    @HklCommand
    def trackphi(self, b=None):
        """trackphi [boolean] -- determines wether phi parameter will track phi axis""" #@IgnorePep8
        self.__checkInputAndSetOrShowParameterTracking('phi', b)

### Motion ###

    _hklcalcCommandHelp.append('Motion')

    #TODO: Messy, inconsistant use of square brackets in usage strings.

    _hklcalcCommandHelp.append(
        'pos hkl [h k l] -- move diffractometer to hkl, or read hkl position. '
        'Use None to hold a value still')

    _hklcalcCommandHelp.append('sim hkl [h k l] -- simulates moving hkl')

    _hklcalcCommandHelp.append(
        'hkl -- shows loads of info about current hkl position')

    @HklCommand
    def sim(self, scn, hkl):
        """sim hkl [h k l] --simulates moving hkl
        """
        sim(scn, hkl, diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS)
