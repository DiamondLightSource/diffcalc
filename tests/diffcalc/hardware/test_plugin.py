from diffcalc.hardware.plugin import HardwareMonitorPlugin
import unittest


class SimpleHardwareMonitorPlugin(HardwareMonitorPlugin):

    def getPosition(self):
        return [1, 2, 3]

    def getEnergy(self):
        return 1.


class TestHardwareMonitorPluginBase(unittest.TestCase):

    def setUp(self):
        self.hardware = SimpleHardwareMonitorPlugin(['a', 'b', 'c'])

    def test__init__AndGetPhysicalAngleNames(self):
        self.assertEquals(self.hardware.getPhysicalAngleNames(),
                          ('a', 'b', 'c'))

    def test__repr__(self):
        print self.hardware.__repr__()

    def testSetGetPosition(self):
        pass

    def testSetGetEnergyWavelength(self):
        pass

    def testGetPositionByName(self):
        self.assertEqual(self.hardware.getPositionByName('c'), 3.)
        self.assertRaises(ValueError, self.hardware.getPositionByName,
                          'not an angle name')

    def testLowerLimitSetAndGet(self):
        self.hardware.setLowerLimit('a', -1)
        self.hardware.setLowerLimit('b', -2)
        self.hardware.setLowerLimit('c', -3)
        self.assertRaises(ValueError, self.hardware.setLowerLimit,
                          'not an angle', 1)
        self.hardware.setLowerLimit('b', None)
        print "Shoule print WARNING:"
        self.hardware.setLowerLimit('b', None)
        self.assertEquals(self.hardware.getLowerLimit('a'), -1)
        self.assertEquals(self.hardware.getLowerLimit('c'), -3)

    def testUpperLimitSetAndGet(self):
        self.hardware.setUpperLimit('a', 1)
        self.hardware.setUpperLimit('b', 2)
        self.hardware.setUpperLimit('c', 3)
        self.assertRaises(ValueError, self.hardware.setUpperLimit,
                          'not an angle', 1)
        self.hardware.setUpperLimit('b', None)
        print "Shoule print WARNING:"
        self.hardware.setUpperLimit('b', None)
        self.assertEquals(self.hardware.getUpperLimit('a'), 1)
        self.assertEquals(self.hardware.getUpperLimit('c'), 3)

    def testIsPositionWithinLimits(self):
        self.hardware.setUpperLimit('a', 1)
        self.hardware.setUpperLimit('b', 2)
        self.hardware.setLowerLimit('a', -1)
        self.assertTrue(self.hardware.isPositionWithinLimits([0, 0, 999]))
        self.assertTrue(self.hardware.isPositionWithinLimits([1, 2, 999]))
        self.assertTrue(self.hardware.isPositionWithinLimits([-1, -999, 999]))
        self.assertFalse(self.hardware.isPositionWithinLimits([1.01, 0, 999]))
        self.assertFalse(self.hardware.isPositionWithinLimits([0, 2.01, 999]))
        self.assertFalse(self.hardware.isPositionWithinLimits([-1.01, 0, 999]))

    def testIsAxisWithinLimits(self):
        self.hardware.setUpperLimit('a', 1)
        self.hardware.setUpperLimit('b', 2)
        self.hardware.setLowerLimit('a', -1)

        self.assertTrue(self.hardware.isAxisValueWithinLimits('a', 0))
        self.assertTrue(self.hardware.isAxisValueWithinLimits('b', 0))
        self.assertTrue(self.hardware.isAxisValueWithinLimits('c', 999))

        self.assertTrue(self.hardware.isAxisValueWithinLimits('a', 1))
        self.assertTrue(self.hardware.isAxisValueWithinLimits('b', 2))
        self.assertTrue(self.hardware.isAxisValueWithinLimits('c', 999))

        self.assertTrue(self.hardware.isAxisValueWithinLimits('a', -1))
        self.assertTrue(self.hardware.isAxisValueWithinLimits('b', -999))

        self.assertFalse(self.hardware.isAxisValueWithinLimits('a', 1.01))
        self.assertFalse(self.hardware.isAxisValueWithinLimits('b', 2.01))
        self.assertFalse(self.hardware.isAxisValueWithinLimits('a', 1.01))

    def setCutAndGetCuts(self):
        self.hardware.setCut('a', 2)
        self.hardware.setCut('b', 2)
        self.hardware.setCut('c', 2)
        self.assertEquals(self.hardware.getCuts(), {'a': 1, 'b': 2, 'c': 3})
        self.assertRaises(KeyError, self.hardware.setCut, 'not_a_key', 1)

    def test__configureCuts(self):
        hardware = SimpleHardwareMonitorPlugin(['a', 'b', 'c'])
        self.assertEquals(hardware.getCuts(),
                          {'a': -180, 'b': -180, 'c': -180})
        hardware = SimpleHardwareMonitorPlugin(['a', 'phi', 'c'])
        self.assertEquals(hardware.getCuts(), {'a': -180, 'phi': 0, 'c': -180})

    def test__configureCutsWithDefaults(self):
        hardware = SimpleHardwareMonitorPlugin(['a', 'b', 'c'],
                                               {'a': 1, 'b': 2})
        self.assertEquals(hardware.getCuts(), {'a': 1, 'b': 2, 'c': -180})
        hardware = SimpleHardwareMonitorPlugin(['a', 'phi', 'c'],
                                               {'a': 1, 'phi': 2})
        self.assertEquals(hardware.getCuts(), {'a': 1, 'phi': 2, 'c': -180})
        self.assertRaises(
            KeyError, SimpleHardwareMonitorPlugin, ['a', 'b', 'c'],
            {'a': 1, 'not_a_key': 2})

    def testCut(self):
        self.assertEquals(self.hardware.cutAngles((1, 2, 3)),
                          (1, 2, 3))
        self.assertEquals(self.hardware.cutAngles((-181, 0, 181)),
                          (179, 0, -179))
        self.assertEquals(self.hardware.cutAngles((-180, 0, 180,)),
                          (-180, 0, 180))
        self.assertEquals(self.hardware.cutAngles((-360, 0, 360)),
                          (0, 0, 0))
