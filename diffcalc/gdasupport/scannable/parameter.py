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
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableBase as ScannableMotionBase


class DiffractionCalculatorParameter(ScannableMotionBase):

    def __init__(self, name, parameterName, parameter_manager):

        self.parameter_manager = parameter_manager
        self.parameterName = parameterName

        self.setName(name)
        self.setInputNames([parameterName])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(3)

    def asynchronousMoveTo(self, value):
        self.parameter_manager.set_constraint(self.parameterName, value)

    def getPosition(self):
        return self.parameter_manager.get_constraint(self.parameterName)

    def isBusy(self):
        return False
