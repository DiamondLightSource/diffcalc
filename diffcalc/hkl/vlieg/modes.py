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
