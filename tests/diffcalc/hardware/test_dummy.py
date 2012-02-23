import unittest

from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin


class TestDummyHardwareMonitorPlugin(unittest.TestCase):

    def setUp(self):
        self.hardware = DummyHardwareMonitorPlugin(
            ['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'])

    def test__init__(self):
        self.assertEquals(self.hardware.getPosition(), [0.] * 6)
        self.assertEquals(self.hardware.getEnergy(), 12.39842)
        self.assertEquals(self.hardware.getWavelength(), 1.)
        self.assertEquals(self.hardware.getPhysicalAngleNames(),
                          ('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))

    def test__repr__(self):
        print self.hardware.__repr__()

    def testSetGetPosition(self):
        pass

    def testSetGetEnergyWavelength(self):
        pass

    def testGetPositionByName(self):
        self.hardware.setPosition([1., 2., 3., 4., 5., 6.])
        self.assertEqual(self.hardware.getPositionByName('gamma'), 3.)
        self.assertRaises(ValueError, self.hardware.getPositionByName,
                          'not an angle name')
