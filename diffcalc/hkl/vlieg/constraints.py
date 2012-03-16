###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from copy import copy

from diffcalc.util import DiffcalcException


class Mode(object):

    def __init__(self, index, name, group, description, parameterNames,
                 implemented=True):
        self.index = index
        self.group = group
        self.name = name
        self.description = description
        self.parameterNames = parameterNames
        self.implemented = implemented

    def __repr__(self):
        return "%i) %s" % (self.index, self.description)

    def __str__(self):
        return self.__repr__()

    def usesParameter(self, name):
        return name in self.parameterNames


class ModeSelector(object):

    def __init__(self, geometry, parameterManager=None,
                 gammaParameterName='gamma'):
        self.parameter_manager = parameterManager
        self._geometry = geometry
        self._gammaParameterName = gammaParameterName
        self._modelist = {}  # indexed by non-contiguous mode number
        self._configureAvailableModes()
        self._selectedIndex = 1

    def setParameterManager(self, manager):
        """
        Required as a ParameterManager and ModelSelector are mutually tied
        together in practice
        """
        self.parameter_manager = manager

    def _configureAvailableModes(self):

        gammaName = self._gammaParameterName

        ml = self._modelist

        ml[0] = Mode(0, '4cFixedw', 'fourc', 'fourc fixed-bandlw',
                     ['alpha', gammaName, 'blw'], False)

        ml[1] = Mode(1, '4cBeq', 'fourc', 'fourc bisecting',
                     ['alpha', gammaName])

        ml[2] = Mode(2, '4cBin', 'fourc', 'fourc incoming',
                     ['alpha', gammaName, 'betain'])

        ml[3] = Mode(3, '4cBout', 'fourc', 'fourc outgoing',
                     ['alpha', gammaName, 'betaout'])

        ml[4] = Mode(4, '4cAzimuth', 'fourc', 'fourc azimuth',
                     ['alpha', gammaName, 'azimuth'], False)

        ml[5] = Mode(5, '4cPhi', 'fourc', 'fourc fixed-phi',
                     ['alpha', gammaName, 'phi'])

        ml[10] = Mode(10, '5cgBeq', 'fivecFixedGamma', 'fivec bisecting',
                      [gammaName])

        ml[11] = Mode(11, '5cgBin', 'fivecFixedGamma', 'fivec incoming',
                      [gammaName, 'betain'])

        ml[12] = Mode(12, '5cgBout', 'fivecFixedGamma', 'fivec outgoing',
                      [gammaName, 'betaout'])

        ml[13] = Mode(13, '5caBeq', 'fivecFixedAlpha', 'fivec bisecting',
                      ['alpha'])

        ml[14] = Mode(14, '5caBin', 'fivecFixedAlpha', 'fivec incoming',
                      ['alpha', 'betain'])

        ml[15] = Mode(15, '5caBout', 'fivecFixedAlpha', 'fivec outgoing',
                      ['alpha', 'betaout'])

        ml[20] = Mode(20, '6czBeq', 'zaxis', 'zaxis bisecting',
                      [])

        ml[21] = Mode(21, '6czBin', 'zaxis', 'zaxis incoming',
                                  ['betain'])

        ml[22] = Mode(22, '6czBout', 'zaxis', 'zaxiz outgoing',
                                  ['betaout'])

    def setModeByIndex(self, index):
        if index in self._modelist:
            self._selectedIndex = index
        else:
            raise DiffcalcException("mode %r is not defined" % index)

    def setModeByName(self, name):
        def findModeWithName(name):
            for index, mode in self._modelist.items():
                if mode.name == name:
                    return index, mode
            raise ValueError

        try:
            index, mode = findModeWithName(name)
        except ValueError:
            raise DiffcalcException(
                'Unknown mode. The diffraction calculator supports these '
                'modeSelector: %s' % self._supportedModes.keys())
        if  self._geometry.supports_mode_group(mode.group):
            self._selectedIndex = index
        else:
            raise DiffcalcException(
                "Mode %s not supported for this diffractometer (%s)." %
                (name, self._geometry.name))

    def getMode(self):
        return self._modelist[self._selectedIndex]

    def reportCurrentMode(self):
        return self.getMode().__str__()

    def reportAvailableModes(self):
        result = ''
        indecis = self._modelist.keys()
        indecis.sort()
        for index in indecis:
            mode = self._modelist[index]
            if self._geometry.supports_mode_group(mode.group):
                paramString = ''
                flags = ''
                pm = self.parameter_manager
                for paramName in pm.getUserChangableParametersForMode(mode):
                    paramString += paramName + ", "
                if paramString:
                    paramString = paramString[:-2]  # remove trailing commas
                if not mode.implemented:
                    flags += "(Not impl.)"
                result += ('%2i) %-15s (%s) %s\n' % (mode.index,
                           mode.description, paramString, flags))
        return result


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

    def set_constraint(self, name, value):
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

    def get_constraint(self, name):
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
            externalAnglePositionArray = self._hardware.get_position()
            externalAngleNames = list(self._hardware.get_axes_names())
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
