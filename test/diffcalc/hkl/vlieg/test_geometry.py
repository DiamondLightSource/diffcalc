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

import random
import unittest
from math import pi

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm
from test.tools import mneq_


from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry, \
    gammaOnArmToBase, gammaOnBaseToArm, SixCircleGeometry, Fivec, Fourc
from diffcalc.hkl.vlieg.geometry import createVliegMatrices
from diffcalc.hkl.vlieg.geometry import VliegPosition
from diffcalc.util import nearlyEqual, radiansEquivilant as radeq


random.seed()  # uses time

TORAD = pi / 180
TODEG = 180 / pi


class TestSixCirclePlugin(object):

    def setup_method(self):
        self.geometry = SixCircleGeometry()

    def testGetName(self):
        assert self.geometry.name == "sixc"

    def testPhysicalAnglesToInternalPosition(self):
        pos = [0, 0, 0, 0, 0, 0]
        expected = self.geometry.physical_angles_to_internal_position(pos)
        assert VliegPosition(*pos) == expected

    def testInternalPositionToPhysicalAngles(self):
        pos = VliegPosition(0, 0, 0, 0, 0, 0)
        result = self.geometry.internal_position_to_physical_angles(pos)
        assert norm(matrix([pos.totuple()]) - matrix([result])) < 0.001

    def testGammaOn(self):
        assert self.geometry.gamma_location == 'base'

    def testSupportsModeGroup(self):
        assert self.geometry.supports_mode_group('fourc')
        assert not self.geometry.supports_mode_group('made up mode')

    def testGetFixedParameters(self):
        self.geometry.fixed_parameters  # check for exceptions

    def isParamaterUnchangable(self):
        assert not self.geometry.isParamaterUnchangable('made up parameter')


class TestSixCircleGammaOnArmGeometry(object):

    def setup_method(self):
        self.geometry = SixCircleGammaOnArmGeometry()

    def testGetName(self):
        assert self.geometry.name == "sixc_gamma_on_arm"

    def testPhysicalAnglesToInternalPosition(self):
        pos = [1, 2, 3, 4, 5, 6]
        expected = self.geometry.physical_angles_to_internal_position(pos)
        assert VliegPosition(*pos) == expected

    def testInternalPositionToPhysicalAngles(self):
        pos = VliegPosition(1, 2, 3, 4, 5, 6)
        result = self.geometry.internal_position_to_physical_angles(pos)
        mneq_(matrix([pos.totuple()]), matrix([result]), 4)

    def testSupportsModeGroup(self):
        assert self.geometry.supports_mode_group('fourc')
        assert not self.geometry.supports_mode_group('made up mode')

    def testGetFixedParameters(self):
        self.geometry.fixed_parameters  # check for exceptions

    def isParamaterUnchangable(self):
        assert not self.geometry.isParamaterUnchangable('made up parameter')


y_vector = matrix([[0], [1], [0]])

TOLERANCE = 1e-5


def armAnglesToLabVector(alpha, delta, gamma):
    [ALPHA, DELTA, GAMMA, _, _, _] = createVliegMatrices(
        alpha, delta, gamma, None, None, None)
    return ALPHA * DELTA * GAMMA * y_vector


def baseAnglesToLabVector(delta, gamma):
    [_, DELTA, GAMMA, _, _, _] = createVliegMatrices(
        None, delta, gamma, None, None, None)
    return GAMMA * DELTA * y_vector


def checkGammaOnArmToBase(alpha, deltaA, gammaA):
        deltaB, gammaB = gammaOnArmToBase(deltaA, gammaA, alpha)

        labA = armAnglesToLabVector(alpha, deltaA, gammaA)
        labB = baseAnglesToLabVector(deltaB, gammaB)
        if not nearlyEqual(labA, labB, TOLERANCE):
            strLabA = ("[%f, %f, %f]" %
                       (labA.get(0, 0), labA.get(1, 0), labA.get(2, 0)))
            strLabB = ("[%f, %f, %f]" %
                       (labB.get(0, 0), labB.get(1, 0), labB.get(2, 0)))
            rep = ("alpha=%f, delta=%f, gamma=%f" %
                   (alpha * TODEG, deltaB * TODEG, gammaB * TODEG))
            raise AssertionError('\nArm-->Base ' + rep + '\n' +
                "arm (delta, gamma) = (%f,%f) <==>\t labA = %s\n" %
                (deltaA * TODEG, gammaA * TODEG, strLabA) +
                "base(delta, gamma) = (%f,%f) <==>\t labB = %s\n" %
                (deltaB * TODEG, gammaB * TODEG, strLabB))


def checkBaseArmBaseReciprocity(alpha, delta_orig, gamma_orig):
        (deltaB, gammaB) = (delta_orig, gamma_orig)
        (deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha)
        (deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha)
        if ((not radeq(deltaB, delta_orig, TOLERANCE)) or
            (not radeq(gammaB, gamma_orig, TOLERANCE))):
            s = "\nBase-Arm-Base reciprocity\n"
            s += 'alpha=%f\n' % (alpha * TODEG,)
            s += ('   (deltaB, gammaB) = (%f, %f)\n' %
                  (delta_orig * TODEG, gamma_orig * TODEG))
            s += (' ->(deltaA, gammaA) = (%f, %f)\n' %
                  (deltaA * TODEG, gammaA * TODEG))
            s += (' ->(deltaB, gammaB) = (%f, %f)\n' %
                  (deltaB * TODEG, gammaB * TODEG))
            raise AssertionError(s)


def checkArmBaseArmReciprocity(alpha, delta_orig, gamma_orig):
    (deltaA, gammaA) = (delta_orig, gamma_orig)
    (deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha)
    (deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha)
    if ((not radeq(deltaA, delta_orig, TOLERANCE)) or
        (not radeq(gammaA, gamma_orig, TOLERANCE))):
        s = "\nArm-Base-Arm reciprocity\n"
        s += "alpha=%f\n" % (alpha * TODEG,)
        s += ("   (deltaA, gammaA) = (%f, %f)\n" %
              (delta_orig * TODEG, gamma_orig * TODEG))
        s += (" ->(deltaB, gammaB) = (%f, %f)\n" %
              (deltaB * TODEG, gammaB * TODEG))
        s += (" ->(deltaA, gammaA) = (%f, %f)\n" %
              (deltaA * TODEG, gammaA * TODEG))
        raise AssertionError(s)


def test_generator_for_cases():
    for alpha in [-89.9, -45, -1, 0, 1, 45, 89.9]:
        for gamma in [-89.9, -46, -45, -44, -1, 0, 1, 44, 45, 46, 89.9]:
            for delta in [-179.9, -135, -91, -89.9, -89, -46, -45, -44, -1, 0,
                          1, 44, 45, 46, 89, 89.9, 91, 135, 179.9]:
                yield (checkGammaOnArmToBase, alpha * TORAD, delta * TORAD,
                       gamma * TORAD)
                yield (checkArmBaseArmReciprocity, alpha * TORAD,
                       delta * TORAD, gamma * TORAD)


class TestFiveCirclePlugin(object):

    def setup_method(self):
        self.geometry = Fivec()

    def testGetName(self):
        assert self.geometry.name == "fivec"

    def testPhysicalAnglesToInternalPosition(self):
        expected = self.geometry.physical_angles_to_internal_position(
            (1, 2, 4, 5, 6))
        assert VliegPosition(1, 2, 0, 4, 5, 6) == expected

    def testInternalPositionToPhysicalAngles(self):
        result = self.geometry.internal_position_to_physical_angles(
            VliegPosition(1, 2, 0, 4, 5, 6))
        assert (norm(matrix([[1, 2, 4, 5, 6]]) - (matrix([list(result)])))
                < 0.001)

    def testSupportsModeGroup(self):
        assert self.geometry.supports_mode_group('fourc')
        assert not self.geometry.supports_mode_group('fivecFixedAlpha')
        assert self.geometry.supports_mode_group('fivecFixedGamma')

    def testGetFixedParameters(self):
        self.geometry.fixed_parameters  # check for exceptions

    def testisParamaterFixed(self):
        assert not self.geometry.parameter_fixed('made up parameter')
        assert self.geometry.parameter_fixed('gamma')


class TestFourCirclePlugin(object):

    def setup_method(self):
        self.geometry = Fourc()

    def testGetName(self):
        assert self.geometry.name == "fourc"

    def testPhysicalAnglesToInternalPosition(self):
        expected = self.geometry.physical_angles_to_internal_position((2, 4, 5, 6))
        assert VliegPosition(0, 2, 0, 4, 5, 6) == expected

    def testInternalPositionToPhysicalAngles(self):
        result = self.geometry.internal_position_to_physical_angles(
            VliegPosition(0, 2, 0, 4, 5, 6))
        assert (norm(matrix([[2, 4, 5, 6]]) - matrix([list(result)]))
                     < 0.001)

    def testSupportsModeGroup(self):
        assert self.geometry.supports_mode_group('fourc')
        assert not self.geometry.supports_mode_group('fivecFixedAlpha')
        assert not self.geometry.supports_mode_group('fivecFixedGamma')

    def testGetFixedParameters(self):
        self.geometry.fixed_parameters  # check for exceptions

    def testisParamaterFixed(self):
        assert not self.geometry.parameter_fixed('made up parameter')
        assert self.geometry.parameter_fixed('gamma')
        assert self.geometry.parameter_fixed('alpha')
