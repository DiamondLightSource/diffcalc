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


from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.mock import MockMotor
from diffcalc.hardware import HardwareCommands
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hardware import HardwareAdapter
from diffcalc.hardware import ScannableHardwareAdapter
from nose.tools import eq_, assert_raises  # @UnresolvedImport
from test.diffcalc.gdasupport.scannable.mockdiffcalc import MockDiffcalc


class SimpleHardwareAdapter(HardwareAdapter):

    def get_position(self):
        return [1, 2, 3]

    def get_energy(self):
        return 1.


class TestHardwareAdapterBase(unittest.TestCase):

    def setUp(self):
        self.hardware = SimpleHardwareAdapter(['a', 'b', 'c'])

    def test__init__Andget_axes_names(self):
        self.assertEquals(self.hardware.get_axes_names(),
                          ('a', 'b', 'c'))

    def test__repr__(self):
        print self.hardware.__repr__()

    def testSetGetPosition(self):
        pass

    def testSetGetEnergyWavelength(self):
        pass

    def testget_position_by_name(self):
        self.assertEqual(self.hardware.get_position_by_name('c'), 3.)
        self.assertRaises(ValueError, self.hardware.get_position_by_name,
                          'not an angle name')

    def testLowerLimitSetAndGet(self):
        self.hardware.set_lower_limit('a', -1)
        self.hardware.set_lower_limit('b', -2)
        self.hardware.set_lower_limit('c', -3)
        self.assertRaises(ValueError, self.hardware.set_lower_limit,
                          'not an angle', 1)
        self.hardware.set_lower_limit('b', None)
        print "Shoule print WARNING:"
        self.hardware.set_lower_limit('b', None)
        self.assertEquals(self.hardware.get_lower_limit('a'), -1)
        self.assertEquals(self.hardware.get_lower_limit('c'), -3)

    def testUpperLimitSetAndGet(self):
        self.hardware.set_upper_limit('a', 1)
        self.hardware.set_upper_limit('b', 2)
        self.hardware.set_upper_limit('c', 3)
        self.assertRaises(ValueError, self.hardware.set_upper_limit,
                          'not an angle', 1)
        self.hardware.set_upper_limit('b', None)
        print "Shoule print WARNING:"
        self.hardware.set_upper_limit('b', None)
        self.assertEquals(self.hardware.get_upper_limit('a'), 1)
        self.assertEquals(self.hardware.get_upper_limit('c'), 3)

    def testis_position_within_limits(self):
        self.hardware.set_upper_limit('a', 1)
        self.hardware.set_upper_limit('b', 2)
        self.hardware.set_lower_limit('a', -1)
        self.assertTrue(self.hardware.is_position_within_limits([0, 0, 999]))
        self.assertTrue(self.hardware.is_position_within_limits([1, 2, 999]))
        self.assertTrue(self.hardware.is_position_within_limits([-1, -999, 999]))
        self.assertFalse(self.hardware.is_position_within_limits([1.01, 0, 999]))
        self.assertFalse(self.hardware.is_position_within_limits([0, 2.01, 999]))
        self.assertFalse(self.hardware.is_position_within_limits([-1.01, 0, 999]))

    def testIsAxisWithinLimits(self):
        self.hardware.set_upper_limit('a', 1)
        self.hardware.set_upper_limit('b', 2)
        self.hardware.set_lower_limit('a', -1)

        self.assertTrue(self.hardware.is_axis_value_within_limits('a', 0))
        self.assertTrue(self.hardware.is_axis_value_within_limits('b', 0))
        self.assertTrue(self.hardware.is_axis_value_within_limits('c', 999))

        self.assertTrue(self.hardware.is_axis_value_within_limits('a', 1))
        self.assertTrue(self.hardware.is_axis_value_within_limits('b', 2))
        self.assertTrue(self.hardware.is_axis_value_within_limits('c', 999))

        self.assertTrue(self.hardware.is_axis_value_within_limits('a', -1))
        self.assertTrue(self.hardware.is_axis_value_within_limits('b', -999))

        self.assertFalse(self.hardware.is_axis_value_within_limits('a', 1.01))
        self.assertFalse(self.hardware.is_axis_value_within_limits('b', 2.01))
        self.assertFalse(self.hardware.is_axis_value_within_limits('a', 1.01))

    def setCutAndGetCuts(self):
        self.hardware.setCut('a', 2)
        self.hardware.setCut('b', 2)
        self.hardware.setCut('c', 2)
        self.assertEquals(self.hardware.get_cuts(), {'a': 1, 'b': 2, 'c': 3})
        self.assertRaises(KeyError, self.hardware.setCut, 'not_a_key', 1)

    def test__configureCuts(self):
        hardware = SimpleHardwareAdapter(['a', 'b', 'c'])
        self.assertEquals(hardware.get_cuts(),
                          {'a': -180, 'b': -180, 'c': -180})
        hardware = SimpleHardwareAdapter(['a', 'phi', 'c'])
        self.assertEquals(hardware.get_cuts(), {'a': -180, 'phi': 0, 'c': -180})

    def test__configureCutsWithDefaults(self):
        hardware = SimpleHardwareAdapter(['a', 'b', 'c'],
                                               {'a': 1, 'b': 2})
        self.assertEquals(hardware.get_cuts(), {'a': 1, 'b': 2, 'c': -180})
        hardware = SimpleHardwareAdapter(['a', 'phi', 'c'],
                                               {'a': 1, 'phi': 2})
        self.assertEquals(hardware.get_cuts(), {'a': 1, 'phi': 2, 'c': -180})
        self.assertRaises(
            KeyError, SimpleHardwareAdapter, ['a', 'b', 'c'],
            {'a': 1, 'not_a_key': 2})

    def testCut(self):
        self.assertEquals(self.hardware.cut_angles((1, 2, 3)),
                          (1, 2, 3))
        self.assertEquals(self.hardware.cut_angles((-181, 0, 181)),
                          (179, 0, -179))
        self.assertEquals(self.hardware.cut_angles((-180, 0, 180,)),
                          (-180, 0, 180))
        self.assertEquals(self.hardware.cut_angles((-360, 0, 360)),
                          (0, 0, 0))


class TestHardwareCommands():

    def setup(self):
        self.hardware = SimpleHardwareAdapter(['a', 'b', 'c'])
        self.commands = HardwareCommands(self.hardware)

    def testSetcut(self):
        print "*******"
        self.commands.setcut()
        print "*******"
        self.commands.setcut('a')
        print "*******"
        self.commands.setcut('a', -181)
        print "*******"
        eq_(self.commands._hardware.get_cuts()['a'], -181)
        assert_raises(
            ValueError, self.commands.setcut, 'a', 'not a number')
        assert_raises(
            KeyError, self.commands.setcut, 'not an axis', 1)

    def test_set_lim(self):
        self.commands.setmin('a', -1)
        print "*******"
        self.commands.setmin()
        print "*******"
        self.commands.setmax()
        print "*******"


class TestDummyHardwareAdapter(unittest.TestCase):

    def setUp(self):
        self.hardware = DummyHardwareAdapter(
            ['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'])

    def test__init__(self):
        self.assertEquals(self.hardware.get_position(), [0.] * 6)
        self.assertEquals(self.hardware.get_energy(), 12.39842)
        self.assertEquals(self.hardware.get_wavelength(), 1.)
        self.assertEquals(self.hardware.get_axes_names(),
                          ('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))

    def test__repr__(self):
        print self.hardware.__repr__()

    def testSetGetPosition(self):
        pass

    def testSetGetEnergyWavelength(self):
        pass

    def testget_position_by_name(self):
        self.hardware.position = [1., 2., 3., 4., 5., 6.]
        self.assertEqual(self.hardware.get_position_by_name('gamma'), 3.)
        self.assertRaises(ValueError, self.hardware.get_position_by_name,
                          'not an angle name')


def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result


class TestGdaHardwareMonitor(unittest.TestCase):

    def setUp(self):
        dummy = createDummyAxes(['a', 'b', 'c', 'd', 'e', 'f'])
        self.grp = ScannableGroup('grp', dummy)
        self.diffhw = DiffractometerScannableGroup('sixc', MockDiffcalc(6),
                                                   self.grp)
        self.energyhw = MockMotor()
        self.hardware = ScannableHardwareAdapter(self.diffhw,
                                                       self.energyhw)

    def test__init__Andget_axes_names(self):
        self.assertEquals(self.hardware.get_axes_names(),
                          ('a', 'b', 'c', 'd', 'e', 'f'))

    def testGetPosition(self):
        self.diffhw.asynchronousMoveTo((1, 2, 3, 4, 5, 6))
        self.assertEqual(self.hardware.get_position(),
                         [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def testGetEnergy(self):
        self.energyhw.asynchronousMoveTo(1.0)
        self.assertEqual(self.hardware.get_energy(), 1.0)

    def testGetWavelength(self):
        self.energyhw.asynchronousMoveTo(1.0)
        self.assertEqual(self.hardware.get_wavelength(), 12.39842 / 1.0)
