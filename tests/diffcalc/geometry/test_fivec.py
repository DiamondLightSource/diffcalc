try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
import unittest
from diffcalc.geometry.fivec import fivec
from diffcalc.utils import Position

class TestFiveCirclePlugin(unittest.TestCase):
    
    def setUp(self):
        self.geometry=fivec()
    
    def testGetName(self):
        self.assertEqual(self.geometry.getName(), "fivec")

    def testPhysicalAnglesToInternalPosition(self):
        self.assert_( Position(1,2,0,4,5,6)==self.geometry.physicalAnglesToInternalPosition((1,2,4,5,6)) )
    
    def testInternalPositionToPhysicalAngles(self):
        result = self.geometry.internalPositionToPhysicalAngles( Position(1,2,0,4,5,6) )
        self.assert_(Matrix([[1,2,4,5,6]]).minus(Matrix([list(result)])).normF()<0.001)
        
#    def testPhysicalAnglesToInternalWrongInput(self):
#        pos = (1,2,3,4,5)
#        self.assertRaises(AssertionError, self.geometry.physicalAnglesToInternal(pos))    
        
#    def internalAnglesToPhysicalWrongInput(self):
#        pos = (1,2,3,4,5,6,7)
#        self.assertRaises(AssertionError, self.geometry.physicalAnglesToInternal(pos))

    
    def testSupportsModeGroup(self):
        self.assertEqual(self.geometry.supportsModeGroup('fourc'), True)
        self.assertEqual(self.geometry.supportsModeGroup('fivecFixedAlpha'), False)            
        self.assertEqual(self.geometry.supportsModeGroup('fivecFixedGamma'), True)
        
    def testGetFixedParameters(self):
        self.geometry.getFixedParameters() # check for exceptions
    
    def testisParamaterFixed(self):
        self.assertEqual(self.geometry.isParameterFixed('made up parameter'), False)
        self.assertEqual(self.geometry.isParameterFixed('gamma'), True)        

