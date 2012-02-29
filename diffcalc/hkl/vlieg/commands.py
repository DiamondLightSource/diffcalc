from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.help import create_command_decorator

_commands = []
command = create_command_decorator(_commands)


class VliegHklCommands(object):
    """Commands to configure hkl mode and parameters.
    """

    def __init__(self, hardware, geometry, hklcalc):
        self._hardware = hardware
        self._geometry = geometry
        self._hklcalc = hklcalc

    def __str__(self):
        return self._hklcalc.__str__()

    @property
    def commands(self):
        return _commands

    _commands.append('Constraints')

    @command
    def hklmode(self, num=None):
        """hklmode {num} -- changes mode or shows current and available modes and all settings""" #@IgnorePep8

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

    @command
    def setpar(self, scannable_or_string=None, val=None):
        """setpar {parameter_scannable {{val}} -- sets or shows a parameter'
        setpar {parameter_name {val}} -- sets or shows a parameter'
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

    @command
    def trackalpha(self, b=None):
        """trackalpha {boolean} -- determines wether alpha parameter will track alpha axis""" #@IgnorePep8
        self.__checkInputAndSetOrShowParameterTracking('alpha', b)

    @command
    def trackgamma(self, b=None):
        """trackgamma {boolean} -- determines wether gamma parameter will track alpha axis""" #@IgnorePep8
        self.__checkInputAndSetOrShowParameterTracking('gamma', b)

    @command
    def trackphi(self, b=None):
        """trackphi {boolean} -- determines wether phi parameter will track phi axis""" #@IgnorePep8
        self.__checkInputAndSetOrShowParameterTracking('phi', b)
