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

from nose.tools import eq_  # @UnresolvedImport
import tempfile
import os.path
import pytest
from math import atan, sqrt
from nose import SkipTest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

import diffcalc.util  # @UnusedImport
from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry,\
    VliegPosition
from diffcalc.hkl.you.geometry import SixCircle
from diffcalc.hardware import DummyHardwareAdapter
from test.tools import assert_iterable_almost_equal, mneq_, arrayeq_
from diffcalc.ub.persistence import UbCalculationNonPersister,\
    UBCalculationJSONPersister
from diffcalc.ub.calcstate import UBCalcStateEncoder
from diffcalc.util import DiffcalcException, MockRawInput, xyz_rotation,\
    TODEG, TORAD, CoordinateConverter
from diffcalc.hkl.vlieg.calc import VliegUbCalcStrategy, vliegAnglesToHkl
from diffcalc.hkl.you.calc import youAnglesToHkl, YouUbCalcStrategy
from test.diffcalc import scenarios
from test.diffcalc.scenarios import YouPositionScenario


diffcalc.util.DEBUG = True


def prepareRawInput(listOfStrings):
    diffcalc.util.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])

from diffcalc import settings



class _UBCommandsBase():

    def setup_method(self):
        names = 'alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'
        self.hardware = DummyHardwareAdapter(names)
        settings.hardware = self.hardware
        self.conv = CoordinateConverter(transform=self.t_matrix)
        self._refineub_matrix = matrix('0.70711   0.70711   0.00000; -0.70711   0.70711   0.00000; 0.00000   0.00000   1.00000')

        from diffcalc.ub import ub
        reload(ub)
        self.ub = ub
        #self.ub.ubcalc = ub.ubcalc
        prepareRawInput([])
        diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True

    def testNewUb(self):
        self.ub.newub('test1')
        eq_(self.ub.ubcalc._state.name, 'test1')
        with pytest.raises(TypeError):
            self.ub.newub(1)

    def testNewUbInteractively(self):
        prepareRawInput(['ubcalcname', 'xtal', '1', '2', '3', '91', '92',
                         '93'])
        self.ub.newub()

    def testLoadub(self):
        with pytest.raises(TypeError):
            self.ub.loadub((1, 2))

    def testSaveubcalcas(self):
        with pytest.raises(TypeError):
            self.ub.saveubas(1)
        with pytest.raises(TypeError):
            self.ub.saveubas((1, 2))
        self.ub.saveubas('blarghh')

    def testUb(self):
        with pytest.raises(TypeError):
            self.ub.showref((1))
        self.ub.ub()
        self.ub.newub('testubcalc')
        self.ub.ub()

    def testSetlat(self):
        # "Exception should result if no UBCalculation started")
        with pytest.raises(DiffcalcException):
            self.ub.setlat('HCl', 2)

        self.ub.newub('testing_setlat')
        with pytest.raises(TypeError):
            self.ub.setlat(1)
        with pytest.raises(TypeError):
            self.ub.setlat(1, 2)
        with pytest.raises(TypeError):
            self.ub.setlat('HCl')
        self.ub.setlat('NaCl', 1.1)
        ubcalc = self.ub.ubcalc
        eq_(('NaCl', 1.1, 1.1, 1.1, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ub.setlat('NaCl', 1.1, 2.2)
        eq_(('NaCl', 1.1, 1.1, 2.2, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ub.setlat('NaCl', 1.1, 2.2, 3.3)
        eq_(('NaCl', 1.1, 2.2, 3.3, 90, 90, 90), ubcalc._state.crystal.getLattice())
        self.ub.setlat('NaCl', 1.1, 2.2, 3.3, 91)
        eq_(('NaCl', 1.1, 2.2, 3.3, 90, 90, 91), ubcalc._state.crystal.getLattice())
        with pytest.raises(TypeError):
            self.ub.setlat(('NaCl', 1.1, 2.2, 3.3, 91, 92))
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
        with pytest.raises(TypeError):
            self.ub.showref((1))
        eq_(self.ub.showref(), None)  # No UBCalculation loaded
        # will be tested, for exceptions at least, implicitly below
        self.ub.newub('testing_showref')
        eq_(self.ub.showref(), None)  # No UBCalculation loaded"

    def testAddref(self):
        with pytest.raises(TypeError):
            self.ub.addref(1)
        with pytest.raises(TypeError):
            self.ub.addref(1, 2)
        with pytest.raises(TypeError):
            self.ub.addref(1, 2, 'blarghh')
        # start new ubcalc
        self.ub.newub('testing_addref')
        reflist = self.ub.ubcalc._state.reflist  # for convenience

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
        reflist = self.ub.ubcalc._state.reflist  # for convenience

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

        reflist = self.ub.ubcalc._state.reflist  # for convenience
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
        with pytest.raises(TypeError):
            self.ub.swapref(1)
        with pytest.raises(TypeError):
            self.ub.swapref(1, 2, 3)
        with pytest.raises(TypeError):
            self.ub.swapref(1, 1.1)
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
        with pytest.raises(IndexError):
            reflist.get_reflection_in_external_angles(1)

    def testShoworient(self):
        with pytest.raises(TypeError):
            self.ub.showorient((1))
        eq_(self.ub.showorient(), None)  # No UBCalculation loaded
        # will be tested, for exceptions at least, implicitly below
        self.ub.newub('testing_showorient')
        eq_(self.ub.showorient(), None)  # No UBCalculation loaded"

    def testAddorient(self):
        with pytest.raises(TypeError):
            self.ub.addorient(1)
        with pytest.raises(TypeError):
            self.ub.addorient(1, 2)
        with pytest.raises(TypeError):
            self.ub.addorient(1, 2, 'blarghh')
        # start new ubcalc
        self.ub.newub('testing_addorient')
        orientlist = self.ub.ubcalc._state.orientlist  # for convenience

        hkl1 = [1.1, 1.2, 1.3]
        hkl2 = [2.1, 2.2, 2.3]
        orient1 = [1.4, 1.5, 1.6]
        orient2 = [2.4, 2.5, 2.6]
        #
        self.ub.addorient(hkl1, orient1)
        result = orientlist.getOrientation(1)
        trans_orient1 = self.conv.transform(matrix([orient1]).T)
        eq_(result[0], hkl1)
        mneq_(matrix([result[1]]), trans_orient1.T)
        eq_(result[2], None)

        self.ub.addorient(hkl2, orient2, 'atag')
        result = orientlist.getOrientation(2)
        trans_orient2 = self.conv.transform(matrix([orient2]).T)
        eq_(result[0], hkl2)
        mneq_(matrix([result[1]]), trans_orient2.T)
        eq_(result[2], 'atag')

    def testAddorientInteractively(self):
        prepareRawInput([])
        # start new ubcalc
        self.ub.newub('testing_addorient')
        orientlist = self.ub.ubcalc._state.orientlist  # for convenience

        hkl1 = [1.1, 1.2, 1.3]
        hkl2 = [2.1, 2.2, 2.3]
        orient1 = [1.4, 1.5, 1.6]
        orient2 = [2.4, 2.5, 2.6]
        #
        prepareRawInput(['1.1', '1.2', '1.3', '1.4', '1.5', '1.6', ''])
        self.ub.addorient()
        result = orientlist.getOrientation(1)
        trans_orient1 = self.conv.transform(matrix([orient1]).T)
        eq_(result[0], hkl1)
        mneq_(matrix([result[1]]), trans_orient1.T)
        eq_(result[2], None)

        prepareRawInput(['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', 'atag'])
        self.ub.addorient()
        result = orientlist.getOrientation(2)
        trans_orient2 = self.conv.transform(matrix([orient2]).T)
        eq_(result[0], hkl2)
        mneq_(matrix([result[1]]), trans_orient2.T)
        eq_(result[2], 'atag')

    def testEditOrientInteractively(self):
        hkl1 = [1.1, 1.2, 1.3]
        hkl2 = [1.1, 1.2, 3.1]
        orient1 = [1.4, 1.5, 1.6]
        orient2 = [2.4, 1.5, 2.6]
        orient2s = ['2.4', '', '2.6']
        self.ub.newub('testing_editorient')
        self.ub.addorient(hkl1, orient1, 'tag1')
        prepareRawInput(['1.1', '', '3.1'] + orient2s + ['newtag',])
        self.ub.editorient(1)

        orientlist = self.ub.ubcalc._state.orientlist
        result = orientlist.getOrientation(1)
        trans_orient2 = self.conv.transform(matrix([orient2]).T)
        eq_(result[0], hkl2)
        mneq_(matrix([result[1]]), trans_orient2.T)
        eq_(result[2], 'newtag')

    def testSwaporient(self):
        with pytest.raises(TypeError):
            self.ub.swaporient(1)
        with pytest.raises(TypeError):
            self.ub.swaporient(1, 2, 3)
        with pytest.raises(TypeError):
            self.ub.swaporient(1, 1.1)
        self.ub.newub('testing_swaporient')
        hkl = [1.1, 1.2, 1.3]
        orient = [1.4, 1.5, 1.6]
        self.ub.addorient(hkl, orient, 'tag1')
        self.ub.addorient(hkl, orient, 'tag2')
        self.ub.addorient(hkl, orient, 'tag3')
        self.ub.swaporient(1, 3)
        self.ub.swaporient(1, 3)
        self.ub.swaporient(3, 1)  # end flipped
        orientlist = self.ub.ubcalc._state.orientlist
        tag1 = orientlist.getOrientation(1)[2]
        tag2 = orientlist.getOrientation(2)[2]
        tag3 = orientlist.getOrientation(3)[2]
        eq_(tag1, 'tag3')
        eq_(tag2, 'tag2')
        eq_(tag3, 'tag1')
        self.ub.swaporient()
        tag1 = orientlist.getOrientation(1)[2]
        tag2 = orientlist.getOrientation(2)[2]
        eq_(tag1, 'tag2')
        eq_(tag2, 'tag3')

    def testDelorient(self):
        self.ub.newub('testing_delorient')
        hkl = [1.1, 1.2, 1.3]
        pos = [1.4, 1.5, 1.6]
        self.ub.addorient(hkl, pos, 'tag1')
        orientlist = self.ub.ubcalc._state.orientlist
        orientlist.getOrientation(1)
        self.ub.delorient(1)
        with pytest.raises(IndexError):
            orientlist.getOrientation(1)

    def testSetu(self):
        # just test calling this method
        #self.ub.setu([[1,2,3],[1,2,3],[1,2,3]])
        self.ub.newub('testsetu')
        setu = self.ub.setu
        with pytest.raises(TypeError):
            setu(1, 2)
        with pytest.raises(TypeError):
            setu(1)
        with pytest.raises(TypeError):
            setu('a')
        with pytest.raises(TypeError):
            setu([1, 2, 3])
        with pytest.raises(TypeError):
            setu([[1, 2, 3], [1, 2, 3], [1, 2]])
        # diffCalcException expected if no lattice set yet
        with pytest.raises(DiffcalcException):
            setu([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
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
        with pytest.raises(TypeError):
            setub(1, 2)
        with pytest.raises(TypeError):
            setub(1)
        with pytest.raises(TypeError):
            setub('a')
        with pytest.raises(TypeError):
            setub([1, 2, 3])
        with pytest.raises(TypeError):
            setub([[1, 2, 3], [1, 2, 3], [1, 2]])
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
        with pytest.raises(TypeError):
            self.ub.calcub(1)  # wrong input
        # no ubcalc started:
        with pytest.raises(DiffcalcException):
            self.ub.calcub()
        self.ub.newub('testcalcub')
        # not enough reflections:
        with pytest.raises(DiffcalcException):
            self.ub.calcub()

        s = scenarios.sessions(settings.Pos)[0]
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

    def testOrientub(self):
        with pytest.raises(TypeError):
            self.ub.orientub(1)  # wrong input
        # no ubcalc started:
        with pytest.raises(DiffcalcException):
            self.ub.orientub()
        self.ub.newub('testorientub')
        # not enough orientations:
        with pytest.raises(DiffcalcException):
            self.ub.orientub()

        s = scenarios.sessions(settings.Pos)[1]
        self.ub.setlat(s.name, *s.lattice)
        r1 = s.ref1
        orient1 = self.conv.transform(matrix('1; 0; 0'), True)
        self.ub.addorient(
            (r1.h, r1.k, r1.l), orient1.T.tolist()[0], r1.tag)
        r2 = s.ref2
        orient2 = self.conv.transform(matrix('0; -1; 0'), True)
        self.ub.addorient(
            (r2.h, r2.k, r2.l), orient2.T.tolist()[0], r2.tag)
        self.ub.orientub()
        mneq_(self.ub.ubcalc.UB, matrix(s.umatrix) * matrix(s.bmatrix),
              4, note="wrong UB matrix after calculating U")

    def testRefineubInteractively(self):
        self.ub.newub('testing_refineubinteractive')
        self.ub.setlat('xtal', 1, 1, 1, 90, 90, 90)
        self.ub.setmiscut(0)
        prepareRawInput(['1', '1', '', 'n', '0', '60', '0', '30', '0', '0', 'y', 'y'])
        self.ub.refineub()
        getLattice = self.ub.ubcalc._state.crystal.getLattice
        eq_(('xtal', sqrt(2.), sqrt(2.), 1, 90, 90, 90), getLattice())
        mneq_(self.ub.ubcalc.U, self.conv.transform(self._refineub_matrix),
              4, note="wrong U matrix after refinement")

    def testRefineubInteractivelyWithPosition(self):
        self.ub.newub('testing_refineubinteractivepos')
        self.ub.setlat('xtal', 1, 1, 1, 90, 90, 90)
        self.ub.setmiscut(0)
        self.hardware.position = [0, 60, 0, 30, 0, 0]
        prepareRawInput(['1', '1', '', 'y', 'y', 'y'])
        self.ub.refineub()
        getLattice = self.ub.ubcalc._state.crystal.getLattice
        eq_(('xtal', sqrt(2.), sqrt(2.), 1, 90, 90, 90), getLattice())
        mneq_(self.ub.ubcalc.U, self.conv.transform(self._refineub_matrix),
              4, note="wrong U matrix after refinement")

    def testRefineubInteractivelyWithHKL(self):
        self.ub.newub('testing_refineubinteractivehkl')
        self.ub.setlat('xtal', 1, 1, 1, 90, 90, 90)
        self.ub.setmiscut(0)
        self.hardware.position = [0, 60, 0, 30, 0, 0]
        prepareRawInput(['y', 'y', 'y'])
        self.ub.refineub([1, 1, 0])
        getLattice = self.ub.ubcalc._state.crystal.getLattice
        eq_(('xtal', sqrt(2.), sqrt(2.), 1, 90, 90, 90), getLattice())
        mneq_(self.ub.ubcalc.U, self.conv.transform(self._refineub_matrix),
              4, note="wrong U matrix after refinement")

    def testRefineub(self):
        self.ub.newub('testing_refineub')
        self.ub.setlat('xtal', 1, 1, 1, 90, 90, 90)
        self.ub.setmiscut(0)
        prepareRawInput(['y', 'y'])
        self.ub.refineub([1, 1, 0], [0, 60, 0, 30, 0, 0])
        getLattice = self.ub.ubcalc._state.crystal.getLattice
        eq_(('xtal', sqrt(2.), sqrt(2.), 1, 90, 90, 90), getLattice())
        mneq_(self.ub.ubcalc.U, self.conv.transform(self._refineub_matrix),
              4, note="wrong U matrix after refinement")

    def testC2th(self):
        self.ub.newub('testc2th')
        self.ub.setlat('cube', 1, 1, 1, 90, 90, 90)
        assert self.ub.c2th((0, 0, 1)) == pytest.approx(60)

    def testHKLangle(self):
        self.ub.newub('testhklangle')
        self.ub.setlat('cube', 1, 1, 1, 90, 90, 90)
        assert self.ub.hklangle((0, 0, 1), (0, 0, 2)) == pytest.approx(0)
        assert self.ub.hklangle((0, 1, 0), (0, 0, 2)) == pytest.approx(90)
        assert self.ub.hklangle((1, 0, 0), (0, 0, 2)) == pytest.approx(90)
        assert self.ub.hklangle((1, 1, 0), (0, 0, 2)) == pytest.approx(90)
        assert self.ub.hklangle((0, 1, 1), (0, 0, 2)) == pytest.approx(45)
        assert self.ub.hklangle((1, 0, 1), (0, 0, 2)) == pytest.approx(45)
        assert self.ub.hklangle((1, 1, 1), (0, 0, 2)) == pytest.approx(atan(sqrt(2))*TODEG)

    def testSigtau(self):
        # sigtau [sig tau]
        with pytest.raises(TypeError):
            self.ub.sigtau(1)
        with pytest.raises(ValueError):
            self.ub.sigtau(1, 'a')
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
        with pytest.raises(TypeError):
            self.ub.setlat('alpha', 'a')
        with pytest.raises(TypeError):
            self.ub.setlat('alpha', 1, 'a')   

    def test_setnphihkl_at_various_phases(self):
        self.ub.setnphi([1, 0, 1])
        self.ub.setnhkl([1, 0, 1])
        self.ub.newub('test')
        self.ub.setnphi([1, 0, 1])
        self.ub.setnhkl([1, 0, 1]) 
        self.ub.setlat('cube', 1, 1, 1, 90, 90, 90)
        self.ub.setnphi([1, 0, 1])
        self.ub.setnhkl([1, 0, 1])
        self.ub.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.ub.setnphi([1, 0, 1])
        self.ub.setnhkl([1, 0, 1])

    def testMiscut(self):
        self.ub.newub('testsetmiscut')
        self.ub.setlat('cube', 1, 1, 1, 90, 90, 90)
        beam_axis = self.conv.transform(matrix('0; 1; 0'), True).T.tolist()[0]
        beam_maxis = self.conv.transform(matrix('0; -1; 0'), True).T.tolist()[0]
        self.ub.setmiscut(self.t_hand * 30, beam_axis)
        mneq_(self.ub.ubcalc._state.reference.n_hkl, matrix('-0.5000000; 0.00000; 0.8660254'))
        self.ub.addmiscut(self.t_hand * 15, beam_axis)
        mneq_(self.ub.ubcalc._state.reference.n_hkl, matrix('-0.7071068; 0.00000; 0.7071068'))
        self.ub.addmiscut(self.t_hand * 45, beam_maxis)
        mneq_(self.ub.ubcalc._state.reference.n_hkl, matrix('0.0; 0.0; 1.0'))


class TestUbCommandsVlieg(_UBCommandsBase):
    
    def setup_method(self):
        settings.ubcalc_persister = UbCalculationNonPersister()
        settings.geometry = SixCircleGammaOnArmGeometry()
        settings.ubcalc_strategy = VliegUbCalcStrategy()
        settings.angles_to_hkl_function = vliegAnglesToHkl
        settings.Pos = VliegPosition
        self.t_matrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.t_hand = 1
        _UBCommandsBase.setup_method(self)


class TestUBCommandsYou(_UBCommandsBase):

    def setup_method(self):
        settings.ubcalc_persister = UbCalculationNonPersister()
        settings.geometry = SixCircle()
        settings.ubcalc_strategy = YouUbCalcStrategy()
        settings.angles_to_hkl_function = youAnglesToHkl
        settings.Pos = YouPositionScenario
        self.t_matrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.t_hand = 1
        _UBCommandsBase.setup_method(self)


class TestUBCommandsCustomGeom(TestUBCommandsYou):

    def setup_method(self):
        settings.ubcalc_persister = UbCalculationNonPersister()
        inv = matrix([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
        self.zrot = xyz_rotation([0, 0 ,1], 30. * TORAD)
        self.t_matrix = inv * self.zrot
        self.t_hand = -1
        settings.geometry = SixCircle(beamline_axes_transform=self.t_matrix)
        settings.ubcalc_strategy = YouUbCalcStrategy()
        settings.angles_to_hkl_function = youAnglesToHkl
        settings.Pos = YouPositionScenario
        _UBCommandsBase.setup_method(self)

    def testSetu(self):
        self.ub.newub('testsetu_custom')
        self.ub.setlat('NaCl', 1.1)
        zrot = xyz_rotation([0, 0 , 1], 30. * TORAD)
        self.ub.setu(zrot.tolist())
        mneq_(self.ub.ubcalc.U, self.conv.transform(self.zrot))

    def testSetuInteractive(self):
        # Interactive functionality already tested
        raise SkipTest()

    def testSetub(self):
        self.ub.newub('testsetub_custom')
        self.ub.setlat('NaCl', 1.1)
        zrot = xyz_rotation([0, 0 , 1], 30. * TORAD)
        self.ub.setu(zrot.tolist())

        mneq_(self.ub.ubcalc.UB, self.conv.transform(self.zrot) * self.ub.ubcalc._state.crystal.B)

    def testSetUbInteractive(self):
        # Interactive functionality already tested
        raise SkipTest()

class TestUbCommandsJsonPersistence(TestUBCommandsYou):

    def setup_method(self):
        settings.ubcalc_persister = self._createPersister()
        settings.geometry = SixCircle()
        settings.ubcalc_strategy = YouUbCalcStrategy()
        settings.angles_to_hkl_function = youAnglesToHkl
        settings.Pos = YouPositionScenario
        self.t_matrix = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.t_hand = 1
        _UBCommandsBase.setup_method(self)

    def _createPersister(self):
        self.tmpdir = tempfile.mkdtemp()
        print self.tmpdir
        self.persister = UBCalculationJSONPersister(self.tmpdir, UBCalcStateEncoder)
        f = open(os.path.join(self.tmpdir, 'unexpected_file'), 'w')
        f.close()
        return self.persister

    def testNewUb(self):
        self.ub.newub('test1')
        self.ub.loadub('test1')
        self.ub.ub()
        
    def test_n_phi_persistance(self):
        self.ub.newub('test1')
        self.ub.setnphi([0, 1, 0])
        arrayeq_(self.ub.ubcalc.n_phi.T.tolist()[0], [0, 1, 0])
        self.ub.loadub('test1')
        arrayeq_(self.ub.ubcalc.n_phi.T.tolist()[0], [0, 1, 0])

