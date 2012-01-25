from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.hkl.vlieg.commands import HklCommands
from diffcalc.ub.commands import UbCommands
from diffcalc.utils import MockRawInput
from mock import Mock
import diffcalc.utils # @UnusedImport to overide raw_input
import unittest
from diffcalc.hkl.vlieg.calcvlieg import VliegHklCalculator
from diffcalc.ub.calculation import UBCalculation

try:
    from gdascripts.pd.dummy_pds import DummyPD #@UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD

   
def prepareRawInput(listOfStrings):
    diffcalc.utils.raw_input = MockRawInput(listOfStrings)

prepareRawInput([])
    
class TestHklCommands(unittest.TestCase):
    
    def setUp(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = DummyHardwareMonitorPlugin(('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))
        self.mock_ubcalc = Mock(spec=UBCalculation) # Used only to get the UBMatrix, tau and sigma
        self.hklcalc = VliegHklCalculator(self.mock_ubcalc, self.geometry, self.hardware, True)
        self.hklcommands = HklCommands(self.hardware, self.geometry, self.hklcalc)
        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True
        prepareRawInput([])

    def testhelphkl(self):
        self.assertRaises(IndexError, self.hklcommands.helphkl, 1)
        self.assertRaises(TypeError, self.hklcommands.helphkl, 'a', 'b')
        self.assertRaises(IndexError, self.hklcommands.helphkl, 'not_a_command')        
        self.hklcommands.helphkl()
        self.hklcommands.helphkl('helphkl')
        
    def testHklmode(self):
        self.assertRaises(TypeError, self.hklcommands.hklmode, 1, 2)
        self.assertRaises(ValueError, self.hklcommands.hklmode, 'unwanted_string')
        print self.hklcommands.hklmode()
        print self.hklcommands.hklmode(1)
        
    def testSetWithString(self):
        self.hklcommands.setpar()
        self.hklcommands.setpar('alpha')
        self.hklcommands.setpar('alpha', 1)
        self.hklcommands.setpar('alpha', 1.1)
        self.assertEqual(self.hklcommands._hklcalc.parameter_manager.getParameter('alpha'), 1.1)
        
    def testSetWithScannable(self):
        alpha = DummyPD('alpha')
        self.hklcommands.setpar(alpha, 1.1)
        self.assertEqual(self.hklcommands._hklcalc.parameter_manager.getParameter('alpha'), 1.1)
