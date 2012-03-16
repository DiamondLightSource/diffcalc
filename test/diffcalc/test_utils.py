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

from diffcalc.hkl.vlieg.geometry import VliegPosition
from diffcalc.util import MockRawInput, \
    getInputWithDefault, differ, nearlyEqual, degreesEquivilant
import diffcalc.util  # @UnusedImport


class TestUtils(unittest.TestCase):

    def testMockRawInput(self):
        raw_input = MockRawInput('a')  # @ReservedAssignment
        self.assertEquals(raw_input('?'), 'a')

        raw_input = MockRawInput(['a', '1234', '1 2 3'])  # @ReservedAssignment
        self.assertEquals(raw_input('?'), 'a')
        self.assertEquals(raw_input('?'), '1234')
        self.assertEquals(raw_input('?'), '1 2 3')
        self.assertRaises(IndexError, raw_input, '?')

        raw_input = MockRawInput(1)  # @ReservedAssignment
        self.assertRaises(TypeError, raw_input, '?')

    def testGetInputWithDefaultWithStrings(self):
        diffcalc.util.raw_input = MockRawInput('reply')
        print">>>"
        self.assertEquals(getInputWithDefault('enter a thing', 'default'),
                          'reply')
        print">>>"
        diffcalc.util.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'),
                          'default')
        print">>>"
        diffcalc.util.raw_input = MockRawInput('1.23 1 a')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'),
                          '1.23 1 a')

    def testGetInputWithDefaultWithNumbers(self):
        diffcalc.util.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', 1), 1.0)

        diffcalc.util.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', 1.23), 1.23)

        diffcalc.util.raw_input = MockRawInput('1')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), 1.0)

        diffcalc.util.raw_input = MockRawInput('1.23')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'),
                          1.23)

    def testGetInputWithDefaultWithLists(self):
        diffcalc.util.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', (1, 2.0, 3.1)),
                          (1.0, 2.0, 3.1))

        diffcalc.util.raw_input = MockRawInput('1 2.0 3.1')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'),
                          [1.0, 2.0, 3.1])

    def testDiffer(self):
        self.assertFalse(differ([1., 2., 3.], [1., 2., 3.], .0000000000000001))
        self.assertFalse(differ(1, 1.0, .000000000000000001))
        self.assertEquals(differ([2., 4., 6.], [1., 2., 3.], .1),
                          '(2.0, 4.0, 6.0)!=(1.0, 2.0, 3.0)')

        self.assertEquals(differ(1., 1.2, .2), False)
        self.assertEquals(differ(1., 1.2, .1999999999999), '1.0!=1.2')
        self.assertEquals(differ(1., 1.2, 1.20000000000001), False)

    def testNearlyEqual(self):
        self.assertTrue(nearlyEqual([1, 2, 3], [1, 2, 3], .000000000000000001))
        self.assertTrue(nearlyEqual(1, 1.0, .000000000000000001))
        self.assertFalse(nearlyEqual([2, 4, 6], [1, 2, 3], .1))

        self.assertTrue(nearlyEqual(1, 1.2, .2))
        self.assertFalse(nearlyEqual(1, 1.2, .1999999999999))
        self.assertTrue(nearlyEqual(1, 1.2, 1.20000000000001))

    def testDegreesEqual(self):
        tol = .001
        self.assertEquals(degreesEquivilant(1, 1, tol), True)
        self.assertEquals(degreesEquivilant(1, -359, tol), True)
        self.assertEquals(degreesEquivilant(359, -1, tol), True)
        self.assertEquals(degreesEquivilant(1.1, 1, tol), False)
        self.assertEquals(degreesEquivilant(1.1, -359, tol), False)
        self.assertEquals(degreesEquivilant(359.1, -1, tol), False)


class TestPosition(unittest.TestCase):

    def testCompare(self):
        # Test the compare method
        pos1 = VliegPosition(1, 2, 3, 4, 5, 6)
        pos2 = VliegPosition(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)

        self.assert_(pos1 == pos1)
        self.assert_(pos1 != pos2)

    def testNearlyEquals(self):
        pos1 = VliegPosition(1, 2, 3, 4, 5, 6)
        pos2 = VliegPosition(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
        self.assert_(pos1.nearlyEquals(pos2, 0.11))
        self.assert_(not pos1.nearlyEquals(pos2, 0.1))

    def testClone(self):
        pos = VliegPosition(1, 2, 3, 4., 5., 6.)
        copy = pos.clone()
        self.assert_(pos == copy)
        pos.alpha = 10
        pos.omega = 4.1
