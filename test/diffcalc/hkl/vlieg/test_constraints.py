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
from diffcalc.util import DiffcalcException
from test.diffcalc.hkl.vlieg.test_calcvlieg import \
    createMockHardwareMonitor, createMockDiffractometerGeometry


class TestParameterManager(unittest.TestCase):

    def setUp(self):
        self.hw = createMockHardwareMonitor()
        self.ms = ModeSelector(createMockDiffractometerGeometry())
        self.pm = VliegParameterManager(createMockDiffractometerGeometry(),
                                        self.hw, self.ms)

    def testDefaultParameterValues(self):
        self.assertEqual(self.pm.get_constraint('alpha'), 0)
        self.assertEqual(self.pm.get_constraint('gamma'), 0)
        self.assertRaises(DiffcalcException, self.pm.get_constraint,
                          'not-a-parameter-name')

    def testSetParameter(self):
        self.pm.set_constraint('alpha', 10.1)
        self.assertEqual(self.pm.get_constraint('alpha'), 10.1)

    def testSetTrackParameter_isParameterChecked(self):
        self.assertEqual(self.pm.isParameterTracked('alpha'), False)
        self.pm.set_constraint('alpha', 9)

        self.pm.setTrackParameter('alpha', True)
        self.assertEqual(self.pm.isParameterTracked('alpha'), True)
        self.assertRaises(DiffcalcException, self.pm.set_constraint, 'alpha', 10)
        self.hw.getPosition.return_value = 888, 11, 999
        self.assertEqual(self.pm.get_constraint('alpha'), 11)

        print self.pm.reportAllParameters()
        print "**"
        print self.ms.reportCurrentMode()
        print self.pm.reportParametersUsedInCurrentMode()

        self.pm.setTrackParameter('alpha', False)
        self.assertEqual(self.pm.isParameterTracked('alpha'), False)
        self.assertEqual(self.pm.get_constraint('alpha'), 11)
        self.hw.getPosition.return_value = 888, 12, 999
        self.assertEqual(self.pm.get_constraint('alpha'), 11)
        self.pm.set_constraint('alpha', 13)
        self.assertEqual(self.pm.get_constraint('alpha'), 13)
