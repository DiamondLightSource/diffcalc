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

try:
    from gda.device.scannable import PseudoDevice
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableBase as PseudoDevice


class ScannableGroup(PseudoDevice):

    def __init__(self, name, motorList):

        self.setName(name)
        # Set input format
        motorNames = []
        for scn in motorList:
            motorNames.append(scn.getName())
        self.setInputNames(motorNames)
        # Set output format
        format = []
        for motor in motorList:
            format.append(motor.getOutputFormat()[0])
        self.setOutputFormat(format)
        self.__motors = motorList

    def asynchronousMoveTo(self, position):
        # if input has any Nones, then replace these with the current positions
        if None in position:
            position = list(position)
            current = self.getPosition()
            for idx, val in enumerate(position):
                if val is None:
                    position[idx] = current[idx]

        for scn, pos in zip(self.__motors, position):
            scn.asynchronousMoveTo(pos)

    def getPosition(self):
        return [scn.getPosition() for scn in self.__motors]

    def isBusy(self):
        for scn in self.__motors:
            if scn.isBusy():
                return True
        return False
