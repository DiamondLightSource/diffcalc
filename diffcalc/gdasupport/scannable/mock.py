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


class MockMotor(ScannableMotionBase):

    def __init__(self, name='mock'):
        self.pos = 0.0
        self._busy = False
        self.name = name

    def asynchronousMoveTo(self, pos):
        self._busy = True
        self.pos = float(pos)

    def getPosition(self):
        return self.pos

    def isBusy(self):
        return self._busy

    def makeNotBusy(self):
        self._busy = False

    def getOutputFormat(self):
        return ['%f']
