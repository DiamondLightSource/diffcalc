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

from math import  pi, tan, sin, atan, cos, atan2

TORAD = pi / 180
TODEG = 180 / pi


class SlaveScannableDriver(object):

    def __init__(self, scannables):
        self.scannables = scannables

    def isBusy(self):
        for scn in self.scannables:
            if scn.isBusy():
                return True
        return False

    def waitWhileBusy(self):
        for scn in self.scannables:
            scn.waitWhileBusy()

    def triggerAsynchronousMove(self, triggerPos):
        nu = self.slaveFromTriggerPos(triggerPos)
        for scn in self.scannables:
            scn.asynchronousMoveTo(nu)

    def getPosition(self):
        return self.scannables[0].getPosition()

    def slaveFromTriggerPos(self, triggerPos):
        raise Exception("Abstract")

    def getScannableNames(self):
        return [scn.name for scn in self.scannables]

    def getScannable(self, name):
        for scn in self.scannables:
            if scn.getName() == name:
                return scn
        return None

    def getOutputFormat(self):
        return [list(scn.outputFormat)[0] for scn in self.scannables]

    def getPositions(self):
        return [float(scn.getPosition()) for scn in self.scannables]


"""
Based on: Elias Vlieg, "A (2+3)-Type Surface Diffractometer: Mergence of the
z-axis and (2+2)-Type Geometries", J. Appl. Cryst. (1998). 31. 198-203
"""


class NuDriverForSixCirclePlugin(SlaveScannableDriver):

    def slaveFromTriggerPos(self, triggerPos):

        alpha, delta, gamma, _, _, _ = triggerPos
        alpha = alpha * TORAD
        delta = delta * TORAD
        gamma = gamma * TORAD

        ### Equation16 RHS ###
        rhs = -1 * tan(gamma - alpha) * sin(delta)
        nu = atan(rhs)  # -pi/2 <= nu <= pi/2
        return nu * TODEG


class NuDriverForWillmottHorizontalGeometry(SlaveScannableDriver):

    """
    Based on: Phillip Willmott, "Angle calculations for a (2+3)-type
    diffractometer: focus on area detectors", J. Appl. Cryst. (2011). 44.
    73-83
    """

    def __init__(self, scannables, area_detector=False):
        SlaveScannableDriver.__init__(self, scannables)
        self.area_detector = area_detector

    def slaveFromTriggerPos(self, triggerPos):

        delta, gamma, omegah, _ = triggerPos
        delta *= TORAD
        gamma *= TORAD
        omegah *= TORAD
        if self.area_detector:
            nu = atan2(sin(delta - omegah), tan(gamma))                  # (66)
        else:
            top = -sin(gamma) * sin(omegah)
            bot = (sin(omegah) * cos(gamma) * sin(delta) +
                   cos(omegah) * cos(delta))
            nu = atan2(top, bot)                                         # (61)

        print 'nu:', nu * TODEG
        return nu * TODEG
