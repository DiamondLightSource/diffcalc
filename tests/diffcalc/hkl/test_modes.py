import unittest
from diffcalc.hkl.modes import ModeSelector
from tests.diffcalc.hkl.test_calcvlieg import createMockDiffractometerGeometry
from diffcalc.hkl.parameters import ParameterManager

class TestModeSelector(unittest.TestCase):
    
    def setUp(self):
        
        self.ms = ModeSelector(createMockDiffractometerGeometry(), parameterManager=None)
        self.pm = ParameterManager(createMockDiffractometerGeometry(), None, self.ms)
        self.ms.setParameterManager(self.pm)
        
        
    def testSetModeByIndex(self):
        self.ms.setModeByIndex(0);self.assert_(self.ms.getMode().name == '4cFixedw')
        self.ms.setModeByIndex(1);self.assert_(self.ms.getMode().name == '4cBeq')
    
    def testGetMode(self):
        # tested implicetely by testSetmode
        pass
    
    def testShowAvailableModes(self):
        print self.ms.reportAvailableModes()