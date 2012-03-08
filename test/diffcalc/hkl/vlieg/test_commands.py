import unittest

from mock import Mock

import diffcalc.util  # @UnusedImport to overide raw_input
from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hkl.vlieg.commands import VliegHklCommands
from diffcalc.util import MockRawInput
from diffcalc.hkl.vlieg.calcvlieg import VliegHklCalculator
from diffcalc.ub.calculation import UBCalculation

try:
    from gdascripts.pd.dummy_pds import DummyPD  # @UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD


def prepareRawInput(listOfStrings):
    diffcalc.util.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])


class TestHklCommands(unittest.TestCase):

    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        dummy = 'alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'
        self.hardware = DummyHardwareAdapter(dummy)
        self.mock_ubcalc = Mock(spec=UBCalculation)
        self.hklcalc = VliegHklCalculator(self.mock_ubcalc, self.geometry,
                                          self.hardware, True)
        self.hkl = VliegHklCommands(self.hklcalc, self.geometry)
        diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True
        prepareRawInput([])

    def testHklmode(self):
        self.assertRaises(TypeError, self.hkl.hklmode, 1, 2)
        self.assertRaises(
            ValueError, self.hkl.hklmode, 'unwanted_string')
        print self.hkl.hklmode()
        print self.hkl.hklmode(1)

    def testSetWithString(self):
        self.hkl.setpar()
        self.hkl.setpar('alpha')
        self.hkl.setpar('alpha', 1)
        self.hkl.setpar('alpha', 1.1)
        pm = self.hkl._hklcalc.parameter_manager
        self.assertEqual(pm.get('alpha'), 1.1)

    def testSetWithScannable(self):
        alpha = DummyPD('alpha')
        self.hkl.setpar(alpha, 1.1)
        pm = self.hkl._hklcalc.parameter_manager
        self.assertEqual(pm.get('alpha'), 1.1)
