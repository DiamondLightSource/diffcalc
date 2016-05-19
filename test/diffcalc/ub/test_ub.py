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
from nose.tools import eq_  # @UnresolvedImport

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

import diffcalc.util  # @UnusedImport
from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry
from diffcalc.hardware import DummyHardwareAdapter
from test.tools import assert_iterable_almost_equal, mneq_
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.util import DiffcalcException, MockRawInput
from diffcalc.ub.calc import UBCalculation
from diffcalc.hkl.vlieg.calc import VliegUbCalcStrategy
from test.diffcalc import scenarios
import diffcalc.hkl.vlieg.calc


diffcalc.util.DEBUG = True


def prepareRawInput(listOfStrings):
    diffcalc.util.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])

from diffcalc import settings
from diffcalc.hkl.you.geometry import SixCircle
from mock import Mock
from diffcalc.ub.persistence import UbCalculationNonPersister








class TestUbCommands(unittest.TestCase):

    def setUp(self):
        names = 'alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'
        self.hardware = DummyHardwareAdapter(names)
        _geometry = SixCircleGammaOnArmGeometry()
        _ubcalc_persister = UbCalculationNonPersister()
        settings.hardware = self.hardware
        settings.geometry = _geometry
        settings.ubcalc_persister = _ubcalc_persister
        #settings.set_engine_name('vlieg')
        settings.ubcalc_strategy = diffcalc.hkl.vlieg.calc.VliegUbCalcStrategy()
        settings.angles_to_hkl_function = diffcalc.hkl.vlieg.calc.vliegAnglesToHkl
     
        from diffcalc.ub import ub
        reload(ub)
        self.ub = ub
        #self.ub.ubcalc = ub.ubcalc
        prepareRawInput([])
        diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True

    def testNewUb(self):
        self.ub.newub('test1')
        eq_(self.ub.ubcalc._state.name, 'test1')
        self.assertRaises(TypeError, self.ub.newub, 1)

    def testNewUbInteractively(self):
        prepareRawInput(['ubcalcname', 'xtal', '1', '2', '3', '91', '92',
                         '93'])
        self.ub.newub()

    def testLoadub(self):
        self.assertRaises(TypeError, self.ub.loadub, (1, 2))

    def testSaveubcalcas(self):
        self.assertRaises(TypeError, self.ub.saveubas, 1)
        self.assertRaises(TypeError, self.ub.saveubas, (1, 2))
        self.ub.saveubas('blarghh')

    def testUb(self):
        self.assertRaises(TypeError, self.ub.showref, (1))
        self.ub.ub()
        self.ub.newub('testubcalc')
        self.ub.ub()

    def testSetlat(self):
        # "Exception should result if no UBCalculation started")
        self.assertRaises(DiffcalcException, self.ub.setlat, 'HCl', 2)

        self.ub.newub('testing_setlat')
        self.assertRaises(TypeError, self.ub.setlat, 1)
        self.assertRaises(TypeError, self.ub.setlat, 1, 2)
        self.assertRaises(TypeError, self.ub.setlat, 'HCl')
        self.ub.setlat('NaCl', 1.1)
        ubcalc = self.ub.ubcalc
        eq_(('NaCl', 1.1, 1.1, 1.1, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ub.setlat('NaCl', 1.1, 2.2)
        eq_(('NaCl', 1.1, 1.1, 2.2, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ub.setlat('NaCl', 1.1, 2.2, 3.3)
        eq_(('NaCl', 1.1, 2.2, 3.3, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ub.setlat('NaCl', 1.1, 2.2, 3.3, 91)
        eq_(('NaCl', 1.1, 2.2, 3.3, 90, 90, 91), ubcalc._state.crystal.getLattice())
        self.assertRaises(
            TypeError, self.ub.setlat, ('NaCl', 1.1, 2.2, 3.3, 91, 92))
        self.ub.setlat('NaCl', 1.1, 2.2, 3.3, 91, 92, 93)
        assert_iterable_almost_equal(
            ('NaCl', 1.1, 2.2, 3.3, 91, 92, 92.99999999999999),
             ubcalc._state.crystal.getLattice())

    def testSetlatInteractive(self):
        self.ub.newub('testing_setlatinteractive')
        prepareRawInput(['xtal', '1', '2', '3', '91', '92', '93'])
        self.ub.setlat()
        getLattice = self.ub.ubcalc._state.crystal.getLattice
        assert_iterable_almost_equal(getLattice(),
                         ('xtal', 1., 2., 3., 91, 92, 92.999999999999986))

        #Defaults:
        prepareRawInput(['xtal', '', '', '', '', '', ''])
        self.ub.setlat()
        getLattice = self.ub.ubcalc._state.crystal.getLattice
        eq_(getLattice(), ('xtal', 1., 1., 1., 90, 90, 90))

    def testShowref(self):
        self.assertRaises(TypeError, self.ub.showref, (1))
        eq_(self.ub.showref(), None)  # No UBCalculation loaded
        # will be tested, for exceptions at least, implicitely below
        self.ub.newub('testing_showref')
        eq_(self.ub.showref(), None)  # No UBCalculation loaded"

    def testAddref(self):
#        self.assertRaises(TypeError, self.ub.addref)
        self.assertRaises(TypeError, self.ub.addref, 1)
        self.assertRaises(TypeError, self.ub.addref, 1, 2)
        self.assertRaises(TypeError, self.ub.addref, 1, 2, 'blarghh')
        # start new ubcalc
        self.ub.newub('testing_addref')
        reflist = self.ub.ubcalc._state.reflist  # for conveniance

        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos3 = (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
        pos4 = (4.1, 4.2, 4.3, 4.4, 4.5, 4.6)
        #
        self.hardware.energy = 1.10
        self.hardware.position = pos1
        self.ub.addref([1.1, 1.2, 1.3])
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 1.2, 1.3], pos1, 1.10, None))

        self.hardware.energy = 2.10
        self.hardware.position = pos2
        self.ub.addref([2.1, 2.2, 2.3], 'atag')
        result = reflist.get_reflection_in_external_angles(2)
        eq_(result[:-1], ([2.1, 2.2, 2.3], pos2, 2.10, 'atag'))

        self.ub.addref([3.1, 3.2, 3.3], pos3, 3.10)
        result = reflist.get_reflection_in_external_angles(3)
        eq_(result[:-1], ([3.1, 3.2, 3.3], pos3, 3.10, None))

        self.ub.addref([4.1, 4.2, 4.3], pos4, 4.10, 'tag2')
        result = reflist.get_reflection_in_external_angles(4)
        eq_(result[:-1], ([4.1, 4.2, 4.3], pos4, 4.10, 'tag2'))

    def testAddrefInteractively(self):
        prepareRawInput([])
        # start new ubcalc
        self.ub.newub('testing_addref')
        reflist = self.ub.ubcalc._state.reflist  # for conveniance

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
        self.ub.addref()
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 1.2, 1.3], pos1, 1.10, None))

        self.hardware.energy = 2.10
        self.hardware.position = pos2
        prepareRawInput(['2.1', '2.2', '2.3', '', 'atag'])
        self.ub.addref()
        result = reflist.get_reflection_in_external_angles(2)
        eq_(result[:-1], ([2.1, 2.2, 2.3], pos2, 2.10, 'atag'))

        prepareRawInput(['3.1', '3.2', '3.3', 'n'] + pos3s + ['3.10', ''])
        self.ub.addref()
        result = reflist.get_reflection_in_external_angles(3)
        eq_(result[:-1], ([3.1, 3.2, 3.3], pos3, 3.10, None))

        prepareRawInput(['4.1', '4.2', '4.3', 'n'] + pos4s + ['4.10', 'tag2'])
        self.ub.addref()
        result = reflist.get_reflection_in_external_angles(4)
        eq_(result[:-1], ([4.1, 4.2, 4.3], pos4, 4.10, 'tag2'))

    def testEditRefInteractivelyWithCurrentPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        self.ub.newub('testing_editref')
        self.ub.addref([1, 2, 3], pos1, 10, 'tag1')
        self.hardware.energy = 11
        self.hardware.position = pos2
        prepareRawInput(['1.1', '', '3.1', 'y', ''])
        self.ub.editref(1)

        reflist = self.ub.ubcalc._state.reflist  # for conveniance
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 2, 3.1], pos2, 11, 'tag1'))

    def testEditRefInteractivelyWithEditedPosition(self):
        pos1 = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        pos2 = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6)
        pos2s = ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6']
        self.ub.newub('testing_editref')
        self.ub.addref([1, 2, 3], pos1, 10, 'tag1')
        prepareRawInput(['1.1', '', '3.1', 'n'] + pos2s + ['12', 'newtag'])
        self.ub.editref(1)

        reflist = self.ub.ubcalc._state.reflist
        result = reflist.get_reflection_in_external_angles(1)
        eq_(result[:-1], ([1.1, 2, 3.1], pos2, 12, 'newtag'))

    def testSwapref(self):
        self.assertRaises(TypeError, self.ub.swapref, 1)
        self.assertRaises(TypeError, self.ub.swapref, 1, 2, 3)
        self.assertRaises(TypeError, self.ub.swapref, 1, 1.1)
        self.ub.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.ub.addref([1, 2, 3], pos, 10, 'tag1')
        self.ub.addref([1, 2, 3], pos, 10, 'tag2')
        self.ub.addref([1, 2, 3], pos, 10, 'tag3')
        self.ub.swapref(1, 3)
        self.ub.swapref(1, 3)
        self.ub.swapref(3, 1)  # end flipped
        reflist = self.ub.ubcalc._state.reflist
        tag1 = reflist.get_reflection_in_external_angles(1)[3]
        tag2 = reflist.get_reflection_in_external_angles(2)[3]
        tag3 = reflist.get_reflection_in_external_angles(3)[3]
        eq_(tag1, 'tag3')
        eq_(tag2, 'tag2')
        eq_(tag3, 'tag1')
        self.ub.swapref()
        tag1 = reflist.get_reflection_in_external_angles(1)[3]
        tag2 = reflist.get_reflection_in_external_angles(2)[3]
        eq_(tag1, 'tag2')
        eq_(tag2, 'tag3')

    def testDelref(self):
        self.ub.newub('testing_swapref')
        pos = (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
        self.ub.addref([1, 2, 3], pos, 10, 'tag1')
        reflist = self.ub.ubcalc._state.reflist
        reflist.get_reflection_in_external_angles(1)
        self.ub.delref(1)
        self.assertRaises(IndexError, reflist.get_reflection_in_external_angles, 1)

    def testSetu(self):
        # just test calling this method
        #self.ub.setu([[1,2,3],[1,2,3],[1,2,3]])
        self.ub.newub('testsetu')
        setu = self.ub.setu
        self.assertRaises(TypeError, setu, 1, 2)
        self.assertRaises(TypeError, setu, 1)
        self.assertRaises(TypeError, setu, 'a')
        self.assertRaises(TypeError, setu, [1, 2, 3])
        self.assertRaises(TypeError, setu, [[1, 2, 3], [1, 2, 3], [1, 2]])
        # diffCalcException expected if no lattice set yet
        self.assertRaises(DiffcalcException, setu,
                          [[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        self.ub.setlat('NaCl', 1.1)
        setu([[1, 2, 3], [1, 2, 3], [1, 2, 3]])  # check no exceptions only
        setu(((1, 2, 3), (1, 2, 3), (1, 2, 3)))  # check no exceptions only

    def testSetuInteractive(self):
        self.ub.newub('testsetu')
        self.ub.setlat('NaCl', 1.1)

        prepareRawInput(['1 2 3', '4 5 6', '7 8 9'])
        self.ub.setu()
        a = self.ub.ubcalc.U.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        prepareRawInput(['', ' 9 9.9 99', ''])
        self.ub.setu()

        a = self.ub.ubcalc.U.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 0, 0], [9, 9.9, 99], [0, 0, 1]])

    def testSetub(self):
        # just test calling this method
        self.ub.newub('testsetub')
        setub = self.ub.setub
        self.assertRaises(TypeError, setub, 1, 2)
        self.assertRaises(TypeError, setub, 1)
        self.assertRaises(TypeError, setub, 'a')
        self.assertRaises(TypeError, setub, [1, 2, 3])
        self.assertRaises(TypeError, setub, [[1, 2, 3], [1, 2, 3], [1, 2]])
        setub([[1, 2, 3], [1, 2, 3], [1, 2, 3]])  # check no exceptions only
        setub(((1, 2, 3), (1, 2, 3), (1, 2, 3)))  # check no exceptions only

    def testSetUbInteractive(self):
        self.ub.newub('testsetu')
        self.ub.setlat('NaCl', 1.1)

        prepareRawInput(['1 2 3', '4 5 6', '7 8 9'])
        self.ub.setub()
        a = self.ub.ubcalc.UB.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        prepareRawInput(['', ' 9 9.9 99', ''])
        self.ub.setub()
        a = self.ub.ubcalc.UB.tolist()
        eq_([list(a[0]), list(a[1]), list(a[2])],
            [[1, 0, 0], [9, 9.9, 99], [0, 0, 1]])

    def testCalcub(self):
        self.assertRaises(TypeError, self.ub.calcub, 1)  # wrong input
        # no ubcalc started:
        self.assertRaises(DiffcalcException, self.ub.calcub)
        self.ub.newub('testcalcub')
        # not enougth reflections:
        self.assertRaises(DiffcalcException, self.ub.calcub)

        s = scenarios.sessions()[0]
        self.ub.setlat(s.name, *s.lattice)
        r = s.ref1
        self.ub.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        r = s.ref2
        self.ub.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        self.ub.calcub()
        mneq_(self.ub.ubcalc.UB, matrix(s.umatrix) * matrix(s.bmatrix),
              4, note="wrong UB matrix after calculating U")

    def testC2th(self):
        self.ub.newub('testcalcub')
        self.ub.setlat('cube', 1, 1, 1, 90, 90, 90)
        self.assertAlmostEquals(self.ub.c2th((0, 0, 1)), 60)

    def testSigtau(self):
        # sigtau [sig tau]
        self.assertRaises(TypeError, self.ub.sigtau, 1)
        self.assertRaises(ValueError, self.ub.sigtau, 1, 'a')
        self.ub.sigtau(1, 2)
        self.ub.sigtau(1, 2.0)
        eq_(self.ub.ubcalc.sigma, 1)
        eq_(self.ub.ubcalc.tau, 2.0)

    def testSigtauInteractive(self):
        prepareRawInput(['1', '2.'])
        self.ub.sigtau()
        eq_(self.ub.ubcalc.sigma, 1)
        eq_(self.ub.ubcalc.tau, 2.0)
        #Defaults:
        prepareRawInput(['', ''])
        self.hardware.position = [None, None, None, None, 3, 4.]
        self.ub.sigtau()
        eq_(self.ub.ubcalc.sigma, -3.)
        eq_(self.ub.ubcalc.tau, -4.)

    def testSetWithString(self):
        self.assertRaises(TypeError, self.ub.setlat, 'alpha', 'a')
        self.assertRaises(TypeError, self.ub.setlat, 'alpha', 1, 'a')
