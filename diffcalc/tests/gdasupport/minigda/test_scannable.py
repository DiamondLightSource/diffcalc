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

try:
    from gdascripts.pd.dummy_pds import DummyPD  # @UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD

from diffcalc.gdasupport.scannable.mock import MockMotor
from diffcalc.gdasupport.minigda.scannable import \
    SingleFieldDummyScannable
from diffcalc.gdasupport.minigda.scannable import Scannable
from diffcalc.gdasupport.minigda.scannable import ScannableGroup


class TestScannable(object):

    def setup_method(self):
        self.scannable = Scannable()

    def testSomethingUnrelated(self):
        a = SingleFieldDummyScannable('a')
        print isinstance(a, Scannable)


def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result


class TestScannableGroup(object):

    def setup_method(self):
        self.a = MockMotor('a')
        self.b = MockMotor('bbb')
        self.c = MockMotor('c')
        self.sg = ScannableGroup('abc', (self.a, self.b, self.c))

    def testInit(self):
        assert list(self.sg.getInputNames()) == ['a', 'bbb', 'c']
        assert self.sg.getPosition() == [0.0, 0.0, 0.0]

    def testAsynchronousMoveTo(self):
        self.sg.asynchronousMoveTo([1, 2.0, 3])
        assert self.sg.getPosition() == [1.0, 2.0, 3.0]

    def testAsynchronousMoveToWithNones(self):
        self.sg.asynchronousMoveTo([1.0, 2.0, 3.0])
        self.sg.asynchronousMoveTo([None, None, 3.2])
        assert self.sg.getPosition() == [1.0, 2.0, 3.2]

    def testGetPosition(self):
        # implicitely tested above
        pass

    def testIsBusy(self):
        assert not self.sg.isBusy()
        self.sg.asynchronousMoveTo([1.0, 2.0, 3.0])
        assert self.sg.isBusy()
        self.b.makeNotBusy()
        assert self.sg.isBusy()
        self.a.makeNotBusy()
        self.c.makeNotBusy()
        assert not self.sg.isBusy()
