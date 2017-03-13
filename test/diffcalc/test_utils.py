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
import pytest


class TestUtils(object):

    def testMockRawInput(self):
        raw_input = MockRawInput('a')  # @ReservedAssignment
        assert raw_input('?') == 'a'

        raw_input = MockRawInput(['a', '1234', '1 2 3'])  # @ReservedAssignment
        assert raw_input('?') == 'a'
        assert raw_input('?') == '1234'
        assert raw_input('?') == '1 2 3'
        with pytest.raises(IndexError):
            raw_input('?')

        raw_input = MockRawInput(1)  # @ReservedAssignment
        with pytest.raises(TypeError):
            raw_input('?')

    def testGetInputWithDefaultWithStrings(self):
        diffcalc.util.raw_input = MockRawInput('reply')
        print">>>"
        assert getInputWithDefault('enter a thing', 'default') == 'reply'
        print">>>"
        diffcalc.util.raw_input = MockRawInput('')
        assert getInputWithDefault('enter a thing', 'default') == 'default'
        print">>>"
        diffcalc.util.raw_input = MockRawInput('1.23 1 a')
        assert getInputWithDefault('enter a thing', 'default') == '1.23 1 a'

    def testGetInputWithDefaultWithNumbers(self):
        diffcalc.util.raw_input = MockRawInput('')
        assert getInputWithDefault('enter a thing', 1) == 1.0

        diffcalc.util.raw_input = MockRawInput('')
        assert getInputWithDefault('enter a thing', 1.23) == 1.23

        diffcalc.util.raw_input = MockRawInput('1')
        assert getInputWithDefault('enter a thing', 'default') == 1.0

        diffcalc.util.raw_input = MockRawInput('1.23')
        assert getInputWithDefault('enter a thing', 'default') == 1.23

    def testGetInputWithDefaultWithLists(self):
        diffcalc.util.raw_input = MockRawInput('')
        assert (getInputWithDefault('enter a thing', (1, 2.0, 3.1))
                == (1.0, 2.0, 3.1))

        diffcalc.util.raw_input = MockRawInput('1 2.0 3.1')
        assert getInputWithDefault('enter a thing', 'default') == [1.0, 2.0, 3.1]

    def testDiffer(self):
        assert not differ([1., 2., 3.], [1., 2., 3.], .0000000000000001)
        assert not differ(1, 1.0, .000000000000000001)
        assert (differ([2., 4., 6.], [1., 2., 3.], .1)
                == '(2.0, 4.0, 6.0)!=(1.0, 2.0, 3.0)')

        assert not differ(1., 1.2, .2)
        assert differ(1., 1.2, .1999999999999) == '1.0!=1.2'
        assert not differ(1., 1.2, 1.20000000000001)

    def testNearlyEqual(self):
        assert nearlyEqual([1, 2, 3], [1, 2, 3], .000000000000000001)
        assert nearlyEqual(1, 1.0, .000000000000000001)
        assert not nearlyEqual([2, 4, 6], [1, 2, 3], .1)

        assert nearlyEqual(1, 1.2, .2)
        assert not nearlyEqual(1, 1.2, .1999999999999)
        assert nearlyEqual(1, 1.2, 1.20000000000001)

    def testDegreesEqual(self):
        tol = .001
        assert degreesEquivilant(1, 1, tol)
        assert degreesEquivilant(1, -359, tol)
        assert degreesEquivilant(359, -1, tol)
        assert not degreesEquivilant(1.1, 1, tol)
        assert not degreesEquivilant(1.1, -359, tol)
        assert not degreesEquivilant(359.1, -1, tol)


class TestPosition(object):

    def testCompare(self):
        # Test the compare method
        pos1 = VliegPosition(1, 2, 3, 4, 5, 6)
        pos2 = VliegPosition(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)

        assert pos1 == pos1
        assert pos1 != pos2

    def testNearlyEquals(self):
        pos1 = VliegPosition(1, 2, 3, 4, 5, 6)
        pos2 = VliegPosition(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
        assert pos1.nearlyEquals(pos2, 0.11)
        assert not pos1.nearlyEquals(pos2, 0.1)

    def testClone(self):
        pos = VliegPosition(1, 2, 3, 4., 5., 6.)
        copy = pos.clone()
        assert pos == copy
        pos.alpha = 10
        pos.omega = 4.1
