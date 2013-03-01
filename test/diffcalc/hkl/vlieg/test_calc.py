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
from mock import Mock
from test.tools import mneq_

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm

from diffcalc.hkl.vlieg.calc import VliegHklCalculator, \
    _findOmegaAndChiToRotateHchiIntoQalpha, check
from diffcalc.hkl.vlieg.geometry import createVliegMatrices
from diffcalc.util import DiffcalcException
from test.diffcalc import scenarios

TORAD = pi / 180
TODEG = 180 / pi


def createMockUbcalc(UB):
    ubcalc = Mock()
    ubcalc.tau = 0
    ubcalc.sigma = 0
    ubcalc.UB = UB
    ubcalc.reference.n_phi = matrix([[0], [0], [1]])
    return ubcalc


def createMockHardwareMonitor():
    hardware = Mock()
    hardware.get_position.return_value = (0.0, 0.0, 0.0)
    hardware.get_axes_names.return_value = 'madeup', 'alpha', 'gamma'
    return hardware


def createMockDiffractometerGeometry():
    geometry = Mock()
    geometry.parameter_fixed.return_value = False
    geometry.supports_mode_group.return_value = True
    geometry.fixed_parameters = {}
    geometry.name = 'mock'
    geometry.gamma_location = 'arm'
    return geometry


class TestVliegCoreMathBits(unittest.TestCase):

    def setUp(self):
        self.many = [-91, -90, -89, -46, -45, -44, -1,
                     0, 1, 44, 45, 46, 89, 90, 91]
        self.many = (self.many +
                     map(lambda x: x + 180, self.many) +
                     map(lambda x: x - 180, self.many))

    def test_check(self):
        check(True, 'Should not throw')
        self.assertRaises(Exception, check, False, 'string')
        self.assertRaises(
            DiffcalcException, check, False, DiffcalcException('dce'))

        def acallable(toPrint=None):
            if toPrint is None:
                print "Not throwing exception"
            else:
                print toPrint

        check(False, acallable)
        check(False, acallable, 'this should be printed')

    def test__findOmegaAndChiToRotateHchiIntoQalpha_WithIntegerValues(self):
        for omega in self.many:
            for chi in self.many:
                self.try__findOmegaAndChiToRotateHchiIntoQalpha(omega, chi)
                #print str(omega), ",", str(chi)

    def SKIP_findOmegaAndChiToRotateHchiIntoQalpha_WithRandomValues(self):
        for _ in range(10):
            for omega in self.many:
                for chi in self.many:
                    omega = omega + random.uniform(-.001, .001)
                    chi = chi + random.uniform(-.001, .001)
                    self.try__findOmegaAndChiToRotateHchiIntoQalpha(omega, chi)
                    #print str(omega), ",", str(chi)

    def test__findOmegaAndChiToRotateHchiIntoQalpha_WithTrickyOnes(self):
        tricky_ones = [(-45., -180.), (45., -180.), (135., -180.), (2000, 0.),
                       (225., 0.), (225., -180.), (-225., 0.), (-225., 0.),
                       (-225., -180.), (-135., -180.), (89.998894, -44.999218)]
        for omega, chi in tricky_ones:
            self.try__findOmegaAndChiToRotateHchiIntoQalpha(omega, chi)

    def try__findOmegaAndChiToRotateHchiIntoQalpha(self, omega, chi):
        h_chi = matrix([[1], [1], [1]])
        h_chi = h_chi * (1 / norm(h_chi))
        [_, _, _, OMEGA, CHI, _] = createVliegMatrices(
            None, None, None, omega * TORAD, chi * TORAD, None)
        q_alpha = OMEGA * CHI * h_chi
        try:
            omega_calc, chi_calc = _findOmegaAndChiToRotateHchiIntoQalpha(
                h_chi, q_alpha)
        except ValueError, e:
            raise ValueError(str(e) + "\n, resulting from test where omega:%f"
                             " chi%f" % (self.omega, self.chi))
        [_, _, _, OMEGA, CHI, _] = createVliegMatrices(
            None, None, None, omega_calc, chi_calc, None)
        self.assertArraysNearlyEqual(OMEGA * CHI * h_chi, q_alpha, .000001,
                                     "omega: %f chi:%f" % (omega, chi))

    def assertArraysNearlyEqual(self, first, second, tolerance,
                                contextString=''):
        """
        Fail if the norm of the difference between two arrays is greater than
        the given tolerance.
        """
        diff = first - second
        if norm(diff) >= tolerance:
            raise self.failureException(
                '\n%r !=\n %r\ncontext: %s' %
                (first.tolist(), second.tolist(), contextString))


class BaseTestHklCalculator():

    def setSessionAndCalculation(self):
        raise Exception("Abstract")

    def setUp(self):
        self.ac = VliegHklCalculator(None, createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor())
        self.ac.raiseExceptionsIfAnglesDoNotMapBackToHkl = True
        self.setSessionAndCalculation()

    def testAnglesToHkl(self):
        mockUbcalc = createMockUbcalc(
            matrix(self.sess.umatrix) * matrix(self.sess.bmatrix))

        self.ac = VliegHklCalculator(mockUbcalc,
                                     createMockDiffractometerGeometry(),
                                     createMockHardwareMonitor())
        self.ac.raiseExceptionsIfAnglesDoNotMapBackToHkl = True

        # Check the two given reflections
        (hklactual1, params) = self.ac.anglesToHkl(self.sess.ref1.pos,
                                                   self.sess.ref1.wavelength)
        del params
        (hklactual2, params) = self.ac.anglesToHkl(self.sess.ref2.pos,
                                                   self.sess.ref2.wavelength)
        mneq_(matrix([hklactual1]), matrix([self.sess.ref1calchkl]), 3)
        mneq_(matrix([hklactual2]), matrix([self.sess.ref2calchkl]), 3)

        # ... znd in each calculation through the hkl/posiiont pairs
        if self.calc:
            for hkl, pos, param in zip(self.calc.hklList,
                                       self.calc.posList,
                                       self.calc.paramList):
                (hkl_actual, params) = self.ac.anglesToHkl(pos,
                                                        self.calc.wavelength)
                note = ("wrong hkl calcualted for scenario.name=%s, "
                        "calculation.tag=%s\n  expected hkl=(%f,%f,%f)\n"
                        "calculated hkl=(%f,%f,%f)" %
                        (self.sess.name, self.calc.tag, hkl[0], hkl[1], hkl[2],
                         hkl_actual[0], hkl_actual[1], hkl_actual[2]))
                mneq_(matrix([hkl_actual]), matrix([hkl]), 3, note=note)
                print "***anglesToHkl***"
                print "*** ", str(hkl), " ***"
                print params
                print param

    def testHklToAngles(self):
        if self.calc:
            # Configure the angle calculator for this session scenario
            UB = matrix(self.sess.umatrix) * matrix(self.sess.bmatrix)
            mockUbcalc = createMockUbcalc(UB)
            hw = createMockHardwareMonitor()
            ac = VliegHklCalculator(mockUbcalc,
                                    createMockDiffractometerGeometry(), hw)
            ac.raiseExceptionsIfAnglesDoNotMapBackToHkl = True

            ## configure the angle calculator for this calculation
            ac.mode_selector.setModeByName(self.calc.modeToTest)

            # Set fixed parameters
            if self.calc.modeToTest in ('4cBeq', '4cFixedw'):

                #ac.setParameter('alpha', self.calc.alpha )
                ac.parameter_manager.setTrackParameter('alpha', True)
                hw.get_position.return_value = 888, self.calc.alpha, 999
                ac.parameter_manager.set_constraint('gamma', self.calc.gamma)

            # Test each hkl/position pair
            for idx in range(len(self.calc.hklList)):
                hkl = self.calc.hklList[idx]
                expectedpos = self.calc.posList[idx]
                (pos, params) = ac.hklToAngles(hkl[0], hkl[1], hkl[2],
                                               self.calc.wavelength)
                note = ("wrong positions calculated for TestScenario=%s, "
                        "AngleTestScenario=%s, hkl=(%f,%f,%f):\n"
                        "  expected pos=%s;\n"
                        "  returned pos=%s " %
                        (self.sess.name, self.calc.tag, hkl[0], hkl[1], hkl[2],
                         str(expectedpos), str(pos)))
                self.assert_(pos.nearlyEquals(expectedpos, 0.01), note)
                print "*** hklToAngles ***"
                print "*** ", str(hkl), " ***"
                print params
                try:
                    print self.calc.paramList[idx]
                except IndexError:  # Not always specified
                    pass


class TestVliegHklCalculatorSess1NoCalc(
    BaseTestHklCalculator, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session1
        self.calc = None


class TestVliegHklCalculatorSess2Calc0(
    BaseTestHklCalculator, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session2
        self.calc = scenarios.session2.calculations[0]


class TestVliegHklCalculatorSess3Calc0(
    BaseTestHklCalculator, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session3
        self.calc = scenarios.session3.calculations[0]
