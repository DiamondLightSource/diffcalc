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

from __future__ import with_statement

import unittest

from diffcalc.hkl.vlieg.constraints import ModeSelector, VliegParameterManager
from diffcalc.util import DiffcalcException
from test.diffcalc.hkl.vlieg.test_calc import \
    createMockHardwareMonitor, createMockDiffractometerGeometry
import pytest


class TestModeSelector(object):

    def setup_method(self, method):

        self.ms = ModeSelector(createMockDiffractometerGeometry(),
                               parameterManager=None)
        self.pm = VliegParameterManager(createMockDiffractometerGeometry(),
                                        None, self.ms)
        self.ms.setParameterManager(self.pm)

    def testSetModeByIndex(self):
        self.ms.setModeByIndex(0)
        assert self.ms.getMode().name == '4cFixedw'
        self.ms.setModeByIndex(1)
        assert self.ms.getMode().name == '4cBeq'

    def testGetMode(self):
        # tested implicetely by testSetmode
        pass

    def testShowAvailableModes(self):
        print self.ms.reportAvailableModes()


class TestParameterManager(object):

    def setup_method(self, method):
        self.hw = createMockHardwareMonitor()
        self.ms = ModeSelector(createMockDiffractometerGeometry())
        self.pm = VliegParameterManager(createMockDiffractometerGeometry(),
                                        self.hw, self.ms)

    def testDefaultParameterValues(self):
        assert self.pm.get_constraint('alpha') == 0
        assert self.pm.get_constraint('gamma') == 0
        with pytest.raises(DiffcalcException):
            self.pm.get_constraint('not-a-parameter-name')

    def testSetParameter(self):
        self.pm.set_constraint('alpha', 10.1)
        assert self.pm.get_constraint('alpha') == 10.1

    def testSetTrackParameter_isParameterChecked(self):
        assert not self.pm.isParameterTracked('alpha')
        self.pm.set_constraint('alpha', 9)

        self.pm.setTrackParameter('alpha', True)
        assert self.pm.isParameterTracked('alpha') == True
        with pytest.raises(DiffcalcException):
            self.pm.set_constraint('alpha', 10)
        self.hw.get_position.return_value = 888, 11, 999
        assert self.pm.get_constraint('alpha') == 11

        print self.pm.reportAllParameters()
        print "**"
        print self.ms.reportCurrentMode()
        print self.pm.reportParametersUsedInCurrentMode()

        self.pm.setTrackParameter('alpha', False)
        assert not self.pm.isParameterTracked('alpha')
        assert self.pm.get_constraint('alpha') == 11
        self.hw.get_position.return_value = 888, 12, 999
        assert self.pm.get_constraint('alpha') == 11
        self.pm.set_constraint('alpha', 13)
        assert self.pm.get_constraint('alpha') == 13
