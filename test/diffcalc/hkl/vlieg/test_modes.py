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

from diffcalc.hkl.vlieg.modes import ModeSelector
from diffcalc.hkl.vlieg.parameters import VliegParameterManager
from test.diffcalc.hkl.vlieg.test_calcvlieg import \
    createMockDiffractometerGeometry


class TestModeSelector(unittest.TestCase):

    def setUp(self):

        self.ms = ModeSelector(createMockDiffractometerGeometry(),
                               parameterManager=None)
        self.pm = VliegParameterManager(createMockDiffractometerGeometry(),
                                        None, self.ms)
        self.ms.setParameterManager(self.pm)

    def testSetModeByIndex(self):
        self.ms.setModeByIndex(0)
        self.assert_(self.ms.getMode().name == '4cFixedw')
        self.ms.setModeByIndex(1)
        self.assert_(self.ms.getMode().name == '4cBeq')

    def testGetMode(self):
        # tested implicetely by testSetmode
        pass

    def testShowAvailableModes(self):
        print self.ms.reportAvailableModes()
