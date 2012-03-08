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

import mock
import nose
import unittest

from diffcalc import diffcalc_
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from test.diffcalc.gdasupport.scannable.mockdiffcalc import MockDiffcalc
try:
    from gda.device.scannable.scannablegroup import ScannableGroup
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import ScannableGroup


try:
    from gdascripts.pd.dummy_pds import DummyPD  # @UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD


def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result


PARAM_DICT = {'theta': 1, '2theta': 12., 'Bin': 123., 'Bout': 1234.,
              'azimuth': 12345}


class Popper:

    def __init__(self, *items):
        self.items = list(items)

    def __call__(self, *args):
        return self.items.pop(0)


class TestHkl(unittest.TestCase):

    def setUp(self):
        self.mockDiffcalc = mock.Mock(spec=diffcalc_.Diffcalc)
        self.mockSixc = mock.Mock(spec=DiffractometerScannableGroup)
        self.hkl = Hkl('hkl', self.mockSixc, self.mockDiffcalc)

    def testInit(self):
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 2, 3], PARAM_DICT)
        self.assertEqual(self.hkl.getPosition(), [1, 2, 3])

    def testAsynchronousMoveTo(self):
        self.mockDiffcalc.hkl_to_angles.return_value = ([6, 5, 4, 3, 2, 1],
                                                       None)
        self.hkl.asynchronousMoveTo([1, 0, 1])
        self.mockDiffcalc.hkl_to_angles.assert_called_with(1, 0, 1)
        self.mockSixc.asynchronousMoveTo.assert_called_with([6, 5, 4, 3, 2, 1])

    def testGetPosition(self):
        self.mockSixc.getPosition.return_value = [6, 5, 4, 3, 2, 1]
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1], PARAM_DICT)
        self.assertEqual(self.hkl.getPosition(), [1, 0, 1])
        self.mockDiffcalc.angles_to_hkl.assert_called_with([6, 5, 4, 3, 2, 1])

    def testAsynchronousMoveToWithNonesOutsideScan(self):
        self.mockSixc.getPosition.return_value = [6, 5, 4, 3, 2, 1]
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1],
                                                       PARAM_DICT)
        self.mockDiffcalc.hkl_to_angles.return_value = ([12, 5, 4, 3, 2, 1],
                                                       PARAM_DICT)  # <- 2,0,1

        self.hkl.asynchronousMoveTo([2, 0, None])

        self.mockDiffcalc.angles_to_hkl.assert_called_with([6, 5, 4, 3, 2, 1])
        self.mockDiffcalc.hkl_to_angles.assert_called_with(2, 0, 1)
        self.mockSixc.asynchronousMoveTo.assert_called_with(
            [12, 5, 4, 3, 2, 1])

    def testAsynchronousMoveToWithNonesInScan(self):

        self.mockSixc.getPosition.return_value = [6, 5, 4, 3, 2, 1]
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1], PARAM_DICT)
        self.hkl.atScanStart()
        # should not be used:
        self.mockSixc.getPosition.return_value = [6.1, 5.1, 4.1, 3.1, 2.1, 1.1]
        self.mockDiffcalc.hkl_to_angles.return_value = ([12, 5, 4, 3, 2, 1],
                                                       PARAM_DICT)
        self.hkl.asynchronousMoveTo([2, 0, None])
        # atScanStart:
        self.mockDiffcalc.angles_to_hkl.assert_called_with([6, 5, 4, 3, 2, 1])
        self.mockDiffcalc.hkl_to_angles.assert_called_with(2, 0, 1)
        self.mockSixc.asynchronousMoveTo.assert_called_with(
            [12, 5, 4, 3, 2, 1])

    def testAsynchronousMoveToWithNonesInScanAfterCommandFailure(self):
        # should be forgotten:
        self.mockSixc.getPosition.return_value = [6, 5, 4, 3, 2, 1]
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1], PARAM_DICT)
        self.hkl.atScanStart()
        self.hkl.atCommandFailure()

        self.mockSixc.getPosition.return_value = [6.1, 5.1, 4.1, 3.1, 2.1, 1.1]
        self.mockDiffcalc.hkl_to_angles.return_value = (
                [12.1, 5.1, 4.1, 3.1, 2.1, 1.1], PARAM_DICT)
        self.hkl.asynchronousMoveTo([2, 0, None])

        self.mockDiffcalc.angles_to_hkl.assert_called_with(
            [6.1, 5.1, 4.1, 3.1, 2.1, 1.1])
        self.mockDiffcalc.hkl_to_angles.assert_called_with(2, 0, 1)
        self.mockSixc.asynchronousMoveTo.assert_called_with(
            [12.1, 5.1, 4.1, 3.1, 2.1, 1.1])

    def testAsynchronousMoveToWithNonesInScanAfterAtScanEnd(self):
        self.mockSixc.getPosition.return_value = [6, 5, 4, 3, 2, 1]
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1], PARAM_DICT)
        self.hkl.atScanStart()
        self.hkl.atScanEnd()

        self.mockSixc.getPosition.return_value = [6.1, 5.1, 4.1, 3.1, 2.1, 1.1]
        self.mockDiffcalc.hkl_to_angles.return_value = (
            [12.1, 5.1, 4.1, 3.1, 2.1, 1.1], PARAM_DICT)
        self.hkl.asynchronousMoveTo([2, 0, None])

        self.mockDiffcalc.angles_to_hkl.assert_called_with(
            [6.1, 5.1, 4.1, 3.1, 2.1, 1.1])
        self.mockDiffcalc.hkl_to_angles.assert_called_with(2, 0, 1)
        self.mockSixc.asynchronousMoveTo.assert_called_with(
            [12.1, 5.1, 4.1, 3.1, 2.1, 1.1])

    def testIsBusy(self):
        self.mockSixc.isBusy.return_value = False
        self.assertFalse(self.hkl.isBusy(), False)
        self.mockSixc.isBusy.assert_called()

    def testWaitWhileBusy(self):
        self.hkl.waitWhileBusy()
        self.mockSixc.waitWhileBusy.assert_called()

    def testWhereMoveTo(self):
        # just check for exceptions
        self.mockDiffcalc.hkl_to_angles.return_value = ([6, 5, 4, 3, 2, 1],
                                                       PARAM_DICT)
        self.mockSixc.getName.return_value = 'sixc'
        self.mockSixc.getInputNames.return_value = ['alpha', 'delta', 'gamma',
                                                    'omega', 'chi', 'phi']
        print self.hkl.simulateMoveTo((1.23, 0, 0))

    def testDisp(self):
        print self.hkl.__repr__()


class TestHklReturningVirtualangles(TestHkl):
    def setUp(self):
        TestHkl.setUp(self)
        self.hkl = Hkl('hkl', self.mockSixc, self.mockDiffcalc,
                       ['theta', '2theta', 'Bin', 'Bout', 'azimuth'])

    def testInit(self):
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1], PARAM_DICT)
        self.assertEqual(self.hkl.getPosition(),
                         [1, 0, 1, 1, 12, 123, 1234, 12345])

    def testGetPosition(self):
        self.mockSixc.getPosition.return_value = [6, 5, 4, 3, 2, 1]
        self.mockDiffcalc.angles_to_hkl.return_value = ([1, 0, 1], PARAM_DICT)
        self.assertEqual(self.hkl.getPosition(),
                         [1, 0, 1, 1, 12, 123, 1234, 12345])
        self.mockDiffcalc.angles_to_hkl.assert_called_with([6, 5, 4, 3, 2, 1])


class TestHklWithFailingAngleCalculator(unittest.TestCase):
    def setUp(self):
        class BadMockAngleCalculator:
            def angles_to_hkl(self, pos):
                raise Exception("Problem in angles_to_hkl")

        dummy = createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi',
                                 'phi'])
        self.group = ScannableGroup('grp', dummy)
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup(
            'SixCircleGammaOnArmGeometry', MockDiffcalc(6), self.group)
        self.hkl = Hkl('hkl', self.SixCircleGammaOnArmGeometry,
                       BadMockAngleCalculator())

    def testGetPosition(self):
        self.assertRaises(Exception, self.hkl.getPosition, None)

    def test__repr__(self):
        self.assertEqual(self.hkl.__repr__(), "<hkl: Problem in angles_to_hkl>")

    def test__str__(self):
        self.assertEqual(self.hkl.__str__(), "<hkl: Problem in angles_to_hkl>")

    def testComponentGetPosition(self):
        self.assertRaises(Exception, self.hkl.h.getPosition, None)

    def testComponent__repr__(self):
        raise nose.SkipTest()
        self.assertEqual(self.hkl.h.__repr__(), "<h: Problem in angles_to_hkl>")

    def testComponent__str__(self):
        raise nose.SkipTest()
        self.assertEqual(self.hkl.h.__str__(), "<h: Problem in angles_to_hkl>")
