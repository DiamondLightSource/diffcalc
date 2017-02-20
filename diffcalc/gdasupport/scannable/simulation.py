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

import time
from math import sqrt, pi, exp

try:
    from gda.device.scannable import PseudoDevice
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import \
        ScannableBase as PseudoDevice

from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.hkl.you.calc import youAnglesToHkl
from diffcalc.hkl.vlieg.calc import vliegAnglesToHkl
from diffcalc.hkl.you.geometry import calcCHI, calcPHI

TORAD = pi / 180
TODEG = 180 / pi


class Equation(object):

    def __call__(self, dh, dk, dl):
        raise Exception('Abstract')

    def __str__(self):
        "Abstract equation"


class Gaussian(Equation):

    def __init__(self, variance):
        self.variance = float(variance)

    def __call__(self, dh, dk, dl):
        dr_squared = dh * dh + dk * dk + dl * dl
        return (1 / sqrt(2 * pi * self.variance) *
                exp(-dr_squared / (2 * self.variance)))


class SimulatedCrystalCounter(PseudoDevice):

    def __init__(self, name, diffractometerScannable, geometryPlugin,
                 wavelengthScannable, equation=Gaussian(.01), engine='you'):
        self.setName(name)
        self.setInputNames([name + '_count'])
        self.setOutputFormat(['%7.5f'])
        self.exposureTime = 1
        self.pause = True
        self.diffractometerScannable = diffractometerScannable
        self.geometry = geometryPlugin
        self.wavelengthScannable = wavelengthScannable
        self.equation = equation
        self.engine = engine

        self.cut = None
        self.UB = None
        self.chiMissmount = 0.
        self.phiMissmount = 0.
        self.setCrystal('cubic', 1, 1, 1, 90, 90, 90)

    def setCrystal(self, name, a, b, c, alpha, beta, gamma):
        self.cut = CrystalUnderTest(name, a, b, c, alpha, beta, gamma)
        self.calcUB()

    def setChiMissmount(self, chi):
        self.chiMissmount = chi
        self.calcUB()

    def setPhiMissmount(self, phi):
        self.phiMissmount = phi
        self.calcUB()

    def calcUB(self):
        CHI = calcCHI(self.chiMissmount * TORAD)
        PHI = calcPHI(self.phiMissmount * TORAD)
        self.UB = CHI * PHI * self.cut.B

    def asynchronousMoveTo(self, exposureTime):
        self.exposureTime = exposureTime
        if self.pause:
            time.sleep(exposureTime)  # Should not technically block!

    def getPosition(self):
        h, k, l = self.getHkl()
        dh, dk, dl = h - round(h), k - round(k), l - round(l)
        count = self.equation(dh, dk, dl)
        #return self.exposureTime, count*self.exposureTime
        return count * self.exposureTime

    def getHkl(self):
        pos = self.geometry.physical_angles_to_internal_position(
            self.diffractometerScannable.getPosition())
        pos.changeToRadians()
        wavelength = self.wavelengthScannable.getPosition()
        if self.engine.lower() == 'vlieg':
            return vliegAnglesToHkl(pos, wavelength, self.UB)
        elif self.engine.lower() == 'you':
            return youAnglesToHkl(pos, wavelength, self.UB)
        else:
            raise ValueError(self.engine)

    def isBusy(self):
        return False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = 'simulated crystal detector: %s\n' % self.getName()
        h, k, l = self.getHkl()
        s += '   h : %f\n' % h
        s += '   k : %f\n' % k
        s += '   l : %f\n' % l
        s += self.cut.__str__() + '\n'
        s += "chi orientation: %s\n" % self.chiMissmount
        s += "phi orientation: %s\n" % self.phiMissmount
        ub = self.UB.tolist()
        s += "UB:\n"
        s += "     % 18.13f% 18.13f% 18.12f\n" % (ub[0][0], ub[0][1], ub[0][2])
        s += "     % 18.13f% 18.13f% 18.12f\n" % (ub[1][0], ub[1][1], ub[1][2])
        s += "     % 18.13f% 18.13f% 18.12f\n" % (ub[2][0], ub[2][1], ub[2][2])
        return s
