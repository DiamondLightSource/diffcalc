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

import unittest
from datetime import datetime
from math import cos, sin, pi

from mock import Mock
from nose.tools import raises
try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry
from diffcalc.hkl.vlieg.geometry import VliegPosition as Pos
from test.tools import matrixeq_, mneq_
from diffcalc.ub.calc import UBCalculation
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.util import DiffcalcException
from diffcalc.hkl.vlieg.calc import VliegUbCalcStrategy
from test.diffcalc import scenarios

I = matrix('1 0 0; 0 1 0; 0 0 1')
TORAD = pi / 180



class TestUBCalculationWithSixCircleGammaOnArm(unittest.TestCase):

    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.ubcalc = UBCalculation(
            ('a', 'd', 'g', 'o', 'c', 'p'), self.geometry, UbCalculationNonPersister(),
            VliegUbCalcStrategy())
        self.time = datetime.now()

### State ###

    def testNewCalculation(self):
        self.ubcalc.start_new('testcalc')
        self.assertEqual(self.ubcalc.name, 'testcalc',
                         "Name not set by newCalcualtion")

    @raises(DiffcalcException)
    def testNewCalculationHasNoU(self):
        self.ubcalc.start_new('testcalc')
        print self.ubcalc.U

    @raises(DiffcalcException)
    def testNewCalculationHasNoUB(self):
        self.ubcalc.start_new('testcalc')
        print self.ubcalc.UB

### Lattice ###

    def testSetLattice(self):
        # Not much to test, just make sure no exceptions
        self.ubcalc.start_new('testcalc')
        self.ubcalc.set_lattice('testlattice', 4.0004, 4.0004, 2.27, 90, 90, 90)

### Calculations ###

    def testset_U_manually(self):

        # Test the calculations with U=I
        U = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        for sess in scenarios.sessions():
            self.setUp()
            self.ubcalc.start_new('testcalc')
            self.ubcalc.set_lattice(sess.name, *sess.lattice)
            self.ubcalc.set_U_manually(U)
            # Check the U matrix
            mneq_(self.ubcalc.U, matrix(U), 4,
                  note="wrong U after manually setting U")

            # Check the UB matrix
            if sess.bmatrix is None:
                continue
            print "U: ", U
            print "actual ub: ", self.ubcalc.UB.tolist()
            print " desired b: ", sess.bmatrix
            mneq_(self.ubcalc.UB, matrix(sess.bmatrix), 4,
                  note="wrong UB after manually setting U")

    @raises(DiffcalcException)
    def testGetUMatrix(self):
        self.ubcalc.start_new('testcalc')
        print self.ubcalc.U

    @raises(DiffcalcException)
    def testGetUBMatrix(self):
        self.ubcalc.start_new('testcalc')
        print self.ubcalc.UB

    def testCalculateU(self):

        for sess in scenarios.sessions():
            self.setUp()
            self.ubcalc.start_new('testcalc')
            # Skip this test case unless it contains a umatrix
            if sess.umatrix is None:
                continue

            self.ubcalc.set_lattice(sess.name, *sess.lattice)
            ref1 = sess.ref1
            ref2 = sess.ref2
            t = sess.time
            self.ubcalc.add_reflection(
                ref1.h, ref1.k, ref1.l, ref1.pos, ref1.energy, ref1.tag, t)
            self.ubcalc.add_reflection(
                ref2.h, ref2.k, ref2.l, ref2.pos, ref2.energy, ref2.tag, t)
            self.ubcalc.calculate_UB()
            returned = self.ubcalc.U.tolist()
            print "*Required:"
            print sess.umatrix
            print "*Returned:"
            print returned
            mneq_(self.ubcalc.U, matrix(sess.umatrix), 4,
                  note="wrong U calulated for sess.name=" + sess.name)

    def test__str__(self):
        sess = scenarios.sessions()[0]
        print "***"
        print self.ubcalc.__str__()

        print "***"
        self.ubcalc.start_new('test')
        print self.ubcalc.__str__()

        print "***"
        self.ubcalc.set_lattice(sess.name, *sess.lattice)
        print self.ubcalc.__str__()

        print "***"
        ref1 = sess.ref1
        ref2 = sess.ref2
        t = sess.time
        self.ubcalc.add_reflection(
            ref1.h, ref1.k, ref1.l, ref1.pos, ref1.energy, ref1.tag, t)
        self.ubcalc.add_reflection(
            ref2.h, ref2.k, ref2.l, ref2.pos, ref2.energy, ref2.tag, t)
        print self.ubcalc.__str__()

        print "***"
        self.ubcalc.calculate_UB()
        print self.ubcalc.__str__()


def x_rotation(mu_or_alpha):
    mu_or_alpha *= TORAD
    return matrix(((1, 0, 0),
                   (0, cos(mu_or_alpha), -sin(mu_or_alpha)),
                   (0, sin(mu_or_alpha), cos(mu_or_alpha))))


def y_rotation(chi):
    chi *= TORAD
    return matrix(((cos(chi), 0, sin(chi)),
                   (0, 1, 0),
                   (-sin(chi), 0, cos(chi))))


def z_rotation(th):
    eta = -th * TORAD
    return matrix(((cos(eta), sin(eta), 0),
                   (-sin(eta), cos(eta), 0),
                   (0, 0, 1)))

CUBIC_EN = 12.39842
CUBIC = (1, 1, 1, 90, 90, 90)
ROT = 29


class TestUBCalcWithCubic():

    def setUp(self):
        hardware = Mock()
        hardware.get_axes_names.return_value = \
            ('a', 'd', 'g', 'o', 'c', 'p')
        self.ubcalc = UBCalculation(hardware,
                                    SixCircleGammaOnArmGeometry(),
                                    UbCalculationNonPersister(),
                                    VliegUbCalcStrategy())
        self.ubcalc.start_new('xtalubcalc')
        self.ubcalc.set_lattice("xtal", *CUBIC)
        self.energy = CUBIC_EN

    def addref(self, hklref):
        hkl, position = hklref
        now = datetime.now()
        self.ubcalc.add_reflection(
            hkl[0], hkl[1], hkl[2], position, self.energy, "ref", now)


class TestUBCalcWithCubicTwoRef(TestUBCalcWithCubic):

    def check(self, testname, hklref1, hklref2, expectedUMatrix):
        self.addref(hklref1)
        self.addref(hklref2)
        matrixeq_(expectedUMatrix, self.ubcalc.U)

    def test_with_squarely_mounted(self):
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        lref = ((0, 0, 1),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=0))
        pairs = (("hl", href, lref, I),
                 ("lh", lref, href, I))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u

    def test_with_x_mismount(self):
        U = x_rotation(ROT)
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        kref = ((0, 1, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30 - ROT + 90, chi=90,
                    phi=0))
        lref = ((0, 0, 1),
                Pos(alpha=0, delta=60, gamma=0, omega=30 - ROT, chi=90, phi=0))
        pairs = (("hk", href, kref, U),
                 ("hl", href, lref, U),
                 ("kh", kref, href, U),
                 ("kl", kref, lref, U),
                 ("lk", lref, kref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u

    def test_with_y_mismount(self):
        U = y_rotation(ROT)
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0 - ROT, phi=0))
        lref = ((0, 0, 1),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90 - ROT, phi=0))
        pairs = (("hl", href, lref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u

    def test_with_z_mismount(self):
        U = z_rotation(ROT)
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0 + ROT))
        lref = ((0, 0, 1),  # phi degenerate
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=67))
        pairs = (("hl", href, lref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u

    def test_with_zy_mismount(self):
        U = z_rotation(ROT) * y_rotation(ROT)
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0 - ROT,
                    phi=0 + ROT))
        lref = ((0, 0, 1),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90 - ROT,
                    phi=ROT))  # chi degenerate
        pairs = (("hl", href, lref, U),
                 ("lh", lref, href, U))
        for testname, ref1, ref2, u in pairs:
            yield self.check, testname, ref1, ref2, u


class TestUBCalcWithcubicOneRef(TestUBCalcWithCubic):

    def check(self, testname, hklref, expectedUMatrix):
        print testname
        self.addref(hklref)
        self.ubcalc.calculate_UB_from_primary_only()
        matrixeq_(expectedUMatrix, self.ubcalc.U)

    def test_with_squarely_mounted(self):
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        href_b = ((1, 0, 0),
                  Pos(alpha=0, delta=60, gamma=0, omega=30 + 90, chi=90,
                      phi=-90))
        lref = ((0, 0, 1),  # degenerate in phi
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=67))
        pairs = (("h", href, I),
                 ("hb", href_b, I),
                 ("l", lref, I))
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u

    def test_with_x_mismount(self):
        U = x_rotation(ROT)
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0))
        kref = ((0, 1, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30 - ROT + 90, chi=90,
                    phi=0))
        lref = ((0, 0, 1),
                Pos(alpha=0, delta=60, gamma=0, omega=30 - ROT, chi=90, phi=0))
        pairs = (("h", href, I),  # TODO: can't pass - word instructions
                 ("k", kref, U),
                 ("l", lref, U))
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u

    def test_with_y_mismount(self):
        U = y_rotation(ROT)
        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0 - ROT, phi=0))
        kref = ((0, 1, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30 + 90, chi=90, phi=0))
        lref = ((0, 0, 1),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90 - ROT, phi=0))
        pairs = (("h", href, U),
                 ("k", kref, I),  # TODO: can't pass - word instructions
                 ("l", lref, U))
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u

    def test_with_z_mismount(self):
        U = z_rotation(ROT)

        href = ((1, 0, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0, phi=0 + ROT))
        kref = ((0, 1, 0),
                Pos(alpha=0, delta=60, gamma=0, omega=30 + 90, chi=0,
                    phi=0 + ROT))
        lref = ((0, 0, 1),  # phi degenerate
                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90, phi=67))
        pairs = (("h", href, U),
                 ("k", kref, U),
                 ("l", lref, I))  # TODO: can't pass - word instructions
        for testname, ref, u in pairs:
            yield self.check, testname, ref, u

    #Probably lost cause, conclusion is be careful and return the angle and
    #direction of resulting u matrix
#    def skip_test_with_zy_mismount(self):
#        U = z_rotation(ROT) * y_rotation(ROT)
#        href = ((1, 0, 0),
#                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=0 - ROT,
#                    phi=0 + ROT))
#        kref = ((0, 1, 0),
#                Pos(alpha=0, delta=60, gamma=0, omega=30 + 90, chi=90 - ROT,
#                    phi=0 + ROT))
#        lref = ((0, 0, 1),
#                Pos(alpha=0, delta=60, gamma=0, omega=30, chi=90 - ROT,
#                    phi=ROT))  # chi degenerate
#        pairs = (("h", href, U),
#                 ("k", kref, U),
#                 ("l", lref, U))
#        for testname, ref, u in pairs:
#            yield self.check, testname, ref, u
