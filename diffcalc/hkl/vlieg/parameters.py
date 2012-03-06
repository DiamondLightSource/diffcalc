from copy import copy

from diffcalc.utils import DiffcalcException


class VliegParameterManager(object):

    def __init__(self, geometry, hardware, modeSelector,
                 gammaParameterName='gamma'):
        self._geometry = geometry
        self._hardware = hardware
        self._modeSelector = modeSelector
        self._gammaParameterName = gammaParameterName
        self._parameters = {}
        self._defineParameters()

    def _defineParameters(self):
        # Set default fixed values (In degrees if angles)
        self._parameters = {}
        self._parameters['alpha'] = 0
        self._parameters[self._gammaParameterName] = 0
        self._parameters['blw'] = None  # Busing and Levi omega!
        self._parameters['betain'] = None
        self._parameters['betaout'] = None
        self._parameters['azimuth'] = None
        self._parameters['phi'] = None

        self._parameterDisplayOrder = (
            'alpha', self._gammaParameterName, 'betain', 'betaout', 'azimuth',
            'phi', 'blw')
        self._trackableParameters = ('alpha', self._gammaParameterName, 'phi')
        self._trackedParameters = []

        # Overide parameters that are unchangable for this diffractometer
        for (name, value) in self._geometry.fixed_parameters.items():
            if name not in self._parameters:
                raise RuntimeError(
                    "The %s diffractometer geometry specifies a fixed "
                    "parameter %s that is not used by the diffractometer "
                    "calculator" % (self._geometry.getName, name))
            self._parameters[name] = value

    def reportAllParameters(self):
        self.update_tracked()
        result = ''
        for name in self._parameterDisplayOrder:
            flags = ""
            if not self._modeSelector.getMode().usesParameter(name):
                flags += '(not relevant in this mode)'
            if self._geometry.parameter_fixed(name):
                flags += ' (fixed by this diffractometer)'
            if self.isParameterTracked(name):
                flags += ' (tracking hardware)'
            value = self._parameters[name]
            if value is None:
                value = '---'
            else:
                value = float(value)
            result += '%s: %s %s\n' % (name.rjust(8), value, flags)
        return result

    def reportParametersUsedInCurrentMode(self):
        self.update_tracked()
        result = ''
        for name in self.getUserChangableParametersForMode(
            self._modeSelector.getMode()):
            flags = ""
            value = self._parameters[name]
            if value is None:
                value = '---'
            else:
                value = float(value)
            if self.isParameterTracked(name):
                flags += ' (tracking hardware)'
            result += '%s: %s %s\n' % (name.rjust(8), value, flags)
        return result

    def getUserChangableParametersForMode(self, mode=None):
        """
        (p1,p2...p3) = getUserChangableParametersForMode(mode) returns a list
        of parameters names used in this mode for this diffractometer geometry.
        Checks current mode if no mode specified.
        """
        if mode is None:
            mode = self._mode
        result = []
        for name in self._parameterDisplayOrder:
            if self._isParameterChangeable(name, mode):
                result += [name]
        return result

### Fixed parameters stuff ###

    def setParameter(self, name, value):
        if not name in self._parameters:
            raise DiffcalcException("No fixed parameter %s is used by the "
                                    "diffraction calculator" % name)
        if self._geometry.parameter_fixed(name):
            raise DiffcalcException(
                "The parameter %s cannot be changed: It has been fixed by the "
                "%s diffractometer geometry"
                % (name, self._geometry.name))
        if self.isParameterTracked(name):
            # for safety and to avoid confusion:
            raise DiffcalcException(
                "Cannot change parameter %s as it is set to track an axis.\n"
                "To turn this off use a command like 'trackalpha 0'." % name)

        if not self.isParameterUsedInSelectedMode(name):
            print ("WARNING: The parameter %s is not used in mode %i" %
                   (name, self._modeSelector.getMode().index))
        self._parameters[name] = value

    def isParameterUsedInSelectedMode(self, name):
        return self._modeSelector.getMode().usesParameter(name)

    def getParameterWithoutUpdatingTrackedParemeters(self, name):
        try:
            return self._parameters[name]
        except KeyError:
            raise DiffcalcException("No fixed parameter %s is used by the "
                                    "diffraction calculator" % name)

    def getParameter(self, name):
        self.update_tracked()
        return self.getParameterWithoutUpdatingTrackedParemeters(name)

    def getParameterDict(self):
        self.update_tracked()
        return copy(self._parameters)

    @property
    def settable_constraint_names(self):
        """list of all available constraints that have settable values"""
        return sorted(self.getParameterDict().keys())

    def setTrackParameter(self, name, switch):
        if not name in self._parameters.keys():
            raise DiffcalcException("No fixed parameter %s is used by the "
                                    "diffraction calculator" % name)
        if not name in self._trackableParameters:
            raise DiffcalcException("Parameter %s is not trackable" % name)
        if not self._isParameterChangeable(name):
            print ("WARNING: Parameter %s is not used in mode %i" %
                   (name, self._mode.index))
        if switch:
            if name not in self._trackedParameters:
                self._trackedParameters.append(name)
        else:
            if name in self._trackedParameters:
                self._trackedParameters.remove(name)

    def isParameterTracked(self, name):
        return (name in self._trackedParameters)

    def update_tracked(self):
        """Note that the name of a tracked parameter MUST map into the name of
        an external diffractometer angle
        """
        if self._trackedParameters:
            externalAnglePositionArray = self._hardware.getPosition()
            externalAngleNames = list(self._hardware.getPhysicalAngleNames())
            for name in self._trackedParameters:
                self._parameters[name] = \
                    externalAnglePositionArray[externalAngleNames.index(name)]

    def _isParameterChangeable(self, name, mode=None):
        """
        Returns true if parameter is used in a mode (current mode if none
        specified), AND if it is not locked by the diffractometer geometry
        """
        if mode is None:
            mode = self._modeSelector.getMode()
        return (mode.usesParameter(name) and
                not self._geometry.parameter_fixed(name))
