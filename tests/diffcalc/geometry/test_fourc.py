import unittest

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm

from diffcalc.geometry.fourc import fourc
from diffcalc.hkl.vlieg.position  import VliegPosition


class TestFourCirclePlugin(unittest.TestCase):

    def setUp(self):
        self.geometry = fourc()

    def testGetName(self):
        self.assertEqual(self.geometry.getName(), "fourc")

    def testPhysicalAnglesToInternalPosition(self):
        expected = self.geometry.physicalAnglesToInternalPosition((2, 4, 5, 6))
        self.assert_(VliegPosition(0, 2, 0, 4, 5, 6) == expected)

    def testInternalPositionToPhysicalAngles(self):
        result = self.geometry.internalPositionToPhysicalAngles(
            VliegPosition(0, 2, 0, 4, 5, 6))
        self.assert_(norm(matrix([[2, 4, 5, 6]]) - matrix([list(result)]))
                     < 0.001)

    def testSupportsModeGroup(self):
        self.assertTrue(self.geometry.supportsModeGroup('fourc'))
        self.assertFalse(self.geometry.supportsModeGroup('fivecFixedAlpha'))
        self.assertFalse(self.geometry.supportsModeGroup('fivecFixedGamma'))

    def testGetFixedParameters(self):
        self.geometry.getFixedParameters()  # check for exceptions

    def testisParamaterFixed(self):
        self.assertFalse(self.geometry.isParameterFixed('made up parameter'))
        self.assertTrue(self.geometry.isParameterFixed('gamma'))
        self.assertTrue(self.geometry.isParameterFixed('alpha'))
