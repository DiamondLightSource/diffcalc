from diffcalc.hkl.modes import ModeSelector
from diffcalc.hkl.parameters import ParameterManager
from diffcalc.utils import DiffcalcException
from tests.diffcalc.hkl.test_calcvlieg import createMockHardwareMonitor, \
    createMockDiffractometerGeometry
import unittest

class TestParameterManager(unittest.TestCase):
    
    def setUp(self):
        self.hw = createMockHardwareMonitor()
        self.ms = ModeSelector(createMockDiffractometerGeometry())
        self.pm = ParameterManager(createMockDiffractometerGeometry(), self.hw, self.ms)
        
    def testDefaultParameterValues(self):
        self.assertEqual(self.pm.getParameter('alpha'), 0)
        self.assertEqual(self.pm.getParameter('gamma'), 0)
        self.assertRaises(DiffcalcException, self.pm.getParameter, 'not-a-parameter-name')

    def testSetParameter(self):
        self.pm.setParameter('alpha', 10.1) 
        self.assertEqual(self.pm.getParameter('alpha'), 10.1)
    
    def testSetTrackParameter_isParameterChecked(self):
        self.assertEqual(self.pm.isParameterTracked('alpha'), False)
        self.pm.setParameter('alpha', 9)
        
        self.pm.setTrackParameter('alpha', True)
        self.assertEqual(self.pm.isParameterTracked('alpha'), True)
        self.assertRaises(DiffcalcException, self.pm.setParameter, 'alpha', 10)
        self.hw.getPosition.return_value = 888, 11, 999
        self.assertEqual(self.pm.getParameter('alpha'), 11)
        
        print self.pm.reportAllParameters()
        print "**"
        print self.ms.reportCurrentMode()
        print self.pm.reportParametersUsedInCurrentMode()
        
        self.pm.setTrackParameter('alpha', False)
        self.assertEqual(self.pm.isParameterTracked('alpha'), False)
        self.assertEqual(self.pm.getParameter('alpha'), 11)    
        self.hw.getPosition.return_value = 888, 12, 999
        self.assertEqual(self.pm.getParameter('alpha'), 11)    
        self.pm.setParameter('alpha', 13)
        self.assertEqual(self.pm.getParameter('alpha'), 13)    
