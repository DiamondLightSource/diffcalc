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

from diffcalc.hkl.vlieg.geometry import VliegPosition
from diffcalc.util import MockRawInput, \
    getInputWithDefault, differ, nearlyEqual, degreesEquivilant,\
    CoordinateConverter
import diffcalc.util  # @UnusedImport
import pytest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix


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


class TestCoordinateConverter(object):

    def setup_method(self):
        self.conv = CoordinateConverter(transform=matrix('0 0 1; 1 0 0; 0 1 0'))

    def testVector(self):
        vec100 = matrix('1;0;0')
        vec010 = matrix('0;1;0')
        vec001 = matrix('0;0;1')

        conv100 = self.conv.transform(vec100)
        conv010 = self.conv.transform(vec010)
        conv001 = self.conv.transform(vec001)

        inv100 = self.conv.transform(conv100, True)
        inv010 = self.conv.transform(conv010, True)
        inv001 = self.conv.transform(conv001, True)

        eq_(conv100.tolist(), vec010.tolist())
        eq_(conv010.tolist(), vec001.tolist())
        eq_(conv001.tolist(), vec100.tolist())
        eq_(vec100.tolist(), inv100.tolist())
        eq_(vec010.tolist(), inv010.tolist())
        eq_(vec001.tolist(), inv001.tolist())

    def testVector1m10(self):
        vec110 = matrix(' 1; -1;  0')
        vec011 = matrix(' 0;  1; -1')
        vec101 = matrix('-1;  0;  1')

        conv110 = self.conv.transform(vec110)
        conv011 = self.conv.transform(vec011)
        conv101 = self.conv.transform(vec101)

        inv110 = self.conv.transform(conv110, True)
        inv011 = self.conv.transform(conv011, True)
        inv101 = self.conv.transform(conv101, True)

        eq_(conv110.tolist(), vec011.tolist())
        eq_(conv011.tolist(), vec101.tolist())
        eq_(conv101.tolist(), vec110.tolist())
        eq_(vec110.tolist(), inv110.tolist())
        eq_(vec011.tolist(), inv011.tolist())
        eq_(vec101.tolist(), inv101.tolist())

    def testMatrix(self):
        m = matrix('0 -1 0; 1 0 0; 0 0 -1')
        tm = self.conv.transform(m)
        im = self.conv.transform(tm, True)

        eq_(m.tolist(), im.tolist())

        vec110 = matrix(' 1; -1;  0')
        vec011 = matrix(' 0;  1; -1')
        vec101 = matrix('-1;  0;  1')
        conv110 = self.conv.transform(vec110)
        conv011 = self.conv.transform(vec011)
        conv101 = self.conv.transform(vec101)

        m110 = m * vec110
        m011 = m * vec011
        m101 = m * vec101
        cm110 = tm * conv110
        cm011 = tm * conv011
        cm101 = tm * conv101
        inv110 = self.conv.transform(cm110, True)
        inv011 = self.conv.transform(cm011, True)
        inv101 = self.conv.transform(cm101, True)

        eq_(cm110.tolist(), self.conv.transform(m110).tolist())
        eq_(cm011.tolist(), self.conv.transform(m011).tolist())
        eq_(cm101.tolist(), self.conv.transform(m101).tolist())
        eq_(m110.tolist(), inv110.tolist())
        eq_(m011.tolist(), inv011.tolist())
        eq_(m101.tolist(), inv101.tolist())

    def testVectorFail(self):
        failvec = matrix('0;0;1;0')
        failmarix = matrix('0 0 1; 0 0 1; 1 0 0; 0 0 1')
        with pytest.raises(TypeError):
            CoordinateConverter(transform=failmarix)
        with pytest.raises(TypeError):
            self.conv.transform(failvec)
        with pytest.raises(TypeError):
            self.conv.transform(failmarix)
