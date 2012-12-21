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
from nose.tools import eq_

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

import diffcalc.util  # @UnusedImport
from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry
from diffcalc.hardware import DummyHardwareAdapter
from test.tools import assert_iterable_almost_equal, mneq_
from diffcalc.ub.commands import UbCommands
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.util import DiffcalcException, MockRawInput
from diffcalc.ub.calc import UBCalculation
from diffcalc.hkl.vlieg.calc import VliegUbCalcStrategy
from test.diffcalc import scenarios

diffcalc.util.DEBUG = True


def prepareRawInput(listOfStrings):
    diffcalc.util.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])


class TestUbCommands(unittest.TestCase):

    def setUp(self):
        names = 'alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'
        self.hardware = DummyHardwareAdapter(names)
        self.geometry = SixCircleGammaOnArmGeometry()
        self.ubcalc = UBCalculation(names,
                                    self.geometry,
                                    UbCalculationNonPersister(),
                                    VliegUbCalcStrategy())
        self.ubcommands = UbCommands(self.hardware, self.geometry, self.ubcalc)
        prepareRawInput([])
        diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True

    def testNewUb(self):
        self.ubcommands.newub('test1')
        eq_(self.ubcommands._ubcalc._state.name, 'test1')
        self.assertRaises(TypeError, self.ubcommands.newub, 1)

    def testNewUbInteractively(self):
        prepareRawInput(['ubcalcname', 'xtal', '1', '2', '3', '91', '92',
                         '93'])
        self.ubcommands.newub()

    def testLoadub(self):
        self.assertRaises(TypeError, self.ubcommands.loadub, (1, 2))

    def testSaveubcalcas(self):
        self.assertRaises(TypeError, self.ubcommands.saveubas, 1)
        self.assertRaises(TypeError, self.ubcommands.saveubas, (1, 2))
        self.ubcommands.saveubas('blarghh')

    def testUb(self):
        self.assertRaises(TypeError, self.ubcommands.showref, (1))
        self.ubcommands.ub()
        self.ubcommands.newub('testubcalc')
        self.ubcommands.ub()

    def testSetlat(self):
        # "Exception should result if no UBCalculation started")
        self.assertRaises(DiffcalcException, self.ubcommands.setlat, 'HCl', 2)

        self.ubcommands.newub('testing_setlat')
        self.assertRaises(TypeError, self.ubcommands.setlat, 1)
        self.assertRaises(TypeError, self.ubcommands.setlat, 1, 2)
        self.assertRaises(TypeError, self.ubcommands.setlat, 'HCl')
        self.ubcommands.setlat('NaCl', 1.1)
        ubcalc = self.ubcommands._ubcalc
        eq_(('NaCl', 1.1, 1.1, 1.1, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ubcommands.setlat('NaCl', 1.1, 2.2)
        eq_(('NaCl', 1.1, 1.1, 2.2, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ubcommands.setlat('NaCl', 1.1, 2.2, 3.3)
        eq_(('NaCl', 1.1, 2.2, 3.3, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ubcommands.setlat('NaCl', 1.1, 2.2, 3.3, 91)
        eq_(('NaCl', 1.1, 2.2, 3.3, 90, 90, 91), ubcalc._state.crystal.getLattice())
        self.assertRaises(
            TypeError, self.ubcommands.setlat, ('NaCl', 1.1, 2.2, 3.3, 91, 92))
        self.ubcommands.setlat('NaCl', 1.1, 2.2, 3.3, 91, 92, 93)
        assert_iterable_almost_equal(
            ('NaCl', 1.1, 2.2, 3.3, 91, 92, 92.99999999999999),
             ubcalc._state.crystal.getLattice())

    def testSetlatInteractive(self):
        self.ubcommands.newub('testing_setlatinteractive')
        prepareRawInput(['xtal', '1', '2', '3', '91', '92', '93'])
        self.ubcommands.setlat()
        getLattice = self.ubcommands._ubcalc._state.crystal.getLattice
        assert_iterable_almost_equal(getLattice(),
                         ('xtal', 1., 2., 3., 91, 92, 92.999999999999986))

        #Defaults:
        prepareRawInput(['xtal', '', '', '', '', '', ''])
        self.ubcommands.setlat()
        getLattice = self.ubcommands._ubcalc._state.crystal.getLattice
        eq_(getLattice(), ('xtal', 1., 1., 1., 90, 90, 90))

    def testShowref(self):
        self.assertRaises(TypeError, self.ubcommands.showref, (1))
        eq_(self.ubcommands.showref(), None)  # No UBCalculation loaded
        # will be tested, for exceptions at least, implicitely below
        self.ubcommands.newub('testing_showref')
        eq_(self.ubcommands.showref(), None)  # No UBCalculation loaded"

    def testAddref(self):
#        self.assertRaises(TypeError, self.ubcommands.addref)
        self.assertRaises(TypeError, self.ubcommands.addref, 1)
        self.assertRaises(TypeError, self.ubcommands.addref, 1, 2)
        self.assertRaises(TypeError, self.ubcommands.addref, 1, 2, 'blarghh')
        # start new ubcalc
        self.ubcommands.newub('testing_addref')
        reflist = self.ubcommands._ubcalc._state.reflist  # for conveniance

        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5, 4.6)
        #
        self.hardware.energy = 1.10
        self.hardware.position = pos1
        self.ubcommands.addref([1.1, 1.2, 1.3])
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 1.2, 1.3], pos1, 1.10, None))

        self.hardware.energy = 2.10
        self.hardware.position = pos2
        self.ubcommands.addref([2.1, 2.2, 2.3], 'atag')
        result = reflist.get_reflection_in_external_angles(2)
        eq_(result[:-1], ([2.1, 2.2, 2.3], pos2, 2.10, 'atag'))

        self.ubcommands.addref([3.1, 3.2, 3.3], pos3, 3.10)
        result = reflist.get_reflection_in_external_angles(3)
        eq_(result[:-1], ([3.1, 3.2, 3.3], pos3, 3.10, None))

        self.ubcommands.addref([4.1, 4.2, 4.3], pos4, 4.10, 'tag2')
        result = reflist.get_reflection_in_external_angles(4)
        eq_(result[:-1], ([4.1, 4.2, 4.3], pos4, 4.10, 'tag2'))

    def testAddrefInteractively(self):
        prepareRawInput([])
        # start new ubcalc
        self.ubcommands.newub('testing_addref')
        reflist = self.ubcommands._ubcalc._state.reflist  # for conveniance

        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos3s = ['3.1', '3.2', '3.3', '3.4', '3.5', '3.6']
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5, 4.6)
        pos4s = ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6']
        #
        self.hardware.energy = 1.10
        self.hardware.position = pos1
        prepareRawInput(['1.1', '1.2', '1.3', '', ''])
        self.ubcommands.addref()
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 1.2, 1.3], pos1, 1.10, None))

        self.hardware.energy = 2.10
        self.hardware.position = pos2
        prepareRawInput(['2.1', '2.2', '2.3', '', 'atag'])
        self.ubcommands.addref()
        result = reflist.get_reflection_in_external_angles(2)
        eq_(result[:-1], ([2.1, 2.2, 2.3], pos2, 2.10, 'atag'))

        prepareRawInput(['3.1', '3.2', '3.3', 'n'] + pos3s + ['3.10', ''])
        self.ubcommands.addref()
        result = reflist.get_reflection_in_external_angles(3)
        eq_(result[:-1], ([3.1, 3.2, 3.3], pos3, 3.10, None))

        prepareRawInput(['4.1', '4.2', '4.3', 'n'] + pos4s + ['4.10', 'tag2'])
        self.ubcommands.addref()
        result = reflist.get_reflection_in_external_angles(4)
        eq_(result[:-1], ([4.1, 4.2, 4.3], pos4, 4.10, 'tag2'))

    def testEditRefInteractivelyWithCurrentPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        self.ubcommands.newub('testing_editref')
        self.ubcommands.addref([1, 2, 3], pos1, 10, 'tag1')
        self.hardware.energy = 11
        self.hardware.position = pos2
        prepareRawInput(['1.1', '', '3.1', 'y', ''])
        self.ubcommands.editref(1)

        reflist = self.ubcommands._ubcalc._state.reflist  # for conveniance
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 2, 3.1], pos2, 11, 'tag1'))

    def testEditRefInteractivelyWithEditedPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos2s = ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6']
        self.ubcommands.newub('testing_editref')
        self.ubcommands.addref([1, 2, 3], pos1, 10, 'tag1')
        prepareRawInput(['1.1', '', '3.1', 'n'] + pos2s + ['12', 'newtag'])
        self.ubcommands.editref(1)

        reflist = self.ubcommands._ubcalc._state.reflist
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 2, 3.1], pos2, 12, 'newtag'))

    def testSwapref(self):
        self.assertRaises(TypeError, self.ubcommands.swapref, 1)
        self.assertRaises(TypeError, self.ubcommands.swapref, 1, 2, 3)
        self.assertRaises(TypeError, self.ubcommands.swapref, 1, 1.1)
        self.ubcommands.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.ubcommands.addref([1, 2, 3], pos, 10, 'tag1')
        self.ubcommands.addref([1, 2, 3], pos, 10, 'tag2')
        self.ubcommands.addref([1, 2, 3], pos, 10, 'tag3')
        self.ubcommands.swapref(1, 3)
        self.ubcommands.swapref(1, 3)
        self.ubcommands.swapref(3, 1)  # end flipped
        reflist = self.ubcommands._ubcalc._state.reflist
        tag1 = reflist.get_reflection_in_external_angles(1)[3]
        tag2 = reflist.get_reflection_in_external_angles(2)[3]
        tag3 = reflist.get_reflection_in_external_angles(3)[3]
        eq_(tag1, 'tag3')
        eq_(tag2, 'tag2')
        eq_(tag3, 'tag1')
        self.ubcommands.swapref()
        tag1 = reflist.get_reflection_in_external_angles(1)[3]
        tag2 = reflist.get_reflection_in_external_angles(2)[3]
        eq_(tag1, 'tag2')
        eq_(tag2, 'tag3')

    def testDelref(self):
        self.ubcommands.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.ubcommands.addref([1, 2, 3], pos, 10, 'tag1')
        reflist = self.ubcommands._ubcalc._state.reflist
        reflist.get_reflection_in_external_angles(1)
        self.ubcommands.delref(1)
        self.assertRaises(IndexError, reflist.get_reflection_in_external_angles, 1)

    def testSetu(self):
        # just test calling this method
        #self.ubcommands.setu([[1,2,3],[1,2,3],[1,2,3]])
        self.ubcommands.newub('testsetu')
        setu = self.ubcommands.setu
        self.assertRaises(TypeError, setu, 1, 2)
        self.assertRaises(TypeError, setu, 1)
        self.assertRaises(TypeError, setu, 'a')
        self.assertRaises(TypeError, setu, [1, 2, 3])
        self.assertRaises(TypeError, setu, [[1, 2, 3], [1, 2, 3], [1, 2]])
        # diffCalcException expected if no lattice set yet
        self.assertRaises(DiffcalcException, setu,
                          [[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        self.ubcommands.setlat('NaCl', 1.1)
        setu([[1, 2, 3], [1, 2, 3], [1, 2, 3]])  # check no exceptions only
        setu(((1, 2, 3), (1, 2, 3), (1, 2, 3)))  # check no exceptions only

    def testSetuInteractive(self):
        self.ubcommands.newub('testsetu')
        self.ubcommands.setlat('NaCl', 1.1)

        prepareRawInput(['1 2 3', '4 5 6', '7 8 9'])
        self.ubcommands.setu()
        a = self.ubcalc.U.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        prepareRawInput(['', ' 9 9.9 99', ''])
        self.ubcommands.setu()

        a = self.ubcalc.U.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 0, 0], [9, 9.9, 99], [0, 0, 1]])

    def testSetub(self):
        # just test calling this method
        self.ubcommands.newub('testsetub')
        setub = self.ubcommands.setub
        self.assertRaises(TypeError, setub, 1, 2)
        self.assertRaises(TypeError, setub, 1)
        self.assertRaises(TypeError, setub, 'a')
        self.assertRaises(TypeError, setub, [1, 2, 3])
        self.assertRaises(TypeError, setub, [[1, 2, 3], [1, 2, 3], [1, 2]])
        setub([[1, 2, 3], [1, 2, 3], [1, 2, 3]])  # check no exceptions only
        setub(((1, 2, 3), (1, 2, 3), (1, 2, 3)))  # check no exceptions only

    def testSetUbInteractive(self):
        self.ubcommands.newub('testsetu')
        self.ubcommands.setlat('NaCl', 1.1)

        prepareRawInput(['1 2 3', '4 5 6', '7 8 9'])
        self.ubcommands.setub()
        a = self.ubcalc.UB.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        prepareRawInput(['', ' 9 9.9 99', ''])
        self.ubcommands.setub()
        a = self.ubcalc.UB.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 0, 0], [9, 9.9, 99], [0, 0, 1]])

    def testCalcub(self):
        self.assertRaises(TypeError, self.ubcommands.calcub, 1)  # wrong input
        # no ubcalc started:
        self.assertRaises(DiffcalcException, self.ubcommands.calcub)
        self.ubcommands.newub('testcalcub')
        # not enougth reflections:
        self.assertRaises(DiffcalcException, self.ubcommands.calcub)

        s = scenarios.sessions()[0]
        self.ubcommands.setlat(s.name, *s.lattice)
        r = s.ref1
        self.ubcommands.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        r = s.ref2
        self.ubcommands.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        self.ubcommands.calcub()
        mneq_(self.ubcalc.UB, matrix(s.umatrix) * matrix(s.bmatrix),
              4, note="wrong UB matrix after calculating U")

    def testC2th(self):
        self.ubcommands.newub('testcalcub')
        self.ubcommands.setlat('cube', 1, 1, 1, 90, 90, 90)
        self.assertAlmostEquals(self.ubcommands.c2th((0, 0, 1)), 60)

    def testSigtau(self):
        # sigtau [sig tau]
        self.assertRaises(TypeError, self.ubcommands.sigtau, 1)
        self.assertRaises(ValueError, self.ubcommands.sigtau, 1, 'a')
        self.ubcommands.sigtau(1, 2)
        self.ubcommands.sigtau(1, 2.0)
        eq_(self.ubcalc.sigma, 1)
        eq_(self.ubcalc.tau, 2.0)

    def testSigtauInteractive(self):
        prepareRawInput(['1', '2.'])
        self.ubcommands.sigtau()
        eq_(self.ubcalc.sigma, 1)
        eq_(self.ubcalc.tau, 2.0)
        #Defaults:
        prepareRawInput(['', ''])
        self.hardware.position = [None, None, None, None, 3, 4.]
        self.ubcommands.sigtau()
        eq_(self.ubcalc.sigma, -3.)
        eq_(self.ubcalc.tau, -4.)

    def testSetWithString(self):
        self.assertRaises(TypeError, self.ubcommands.setlat, 'alpha', 'a')
        self.assertRaises(TypeError, self.ubcommands.setlat, 'alpha', 1, 'a')
