from diffcalc.hkl.vlieg.position import VliegPosition
from diffcalc.utils import DiffcalcException, MockRawInput, getInputWithDefault, \
    differ, nearlyEqual, degreesEquivilant
import diffcalc.utils #@UnusedImport
import unittest


class TestUtils(unittest.TestCase):
    
    def testMockRawInput(self):
        raw_input = MockRawInput('a')
        self.assertEquals(raw_input('?'), 'a')    
        
        raw_input = MockRawInput(['a', '1234', '1 2 3'])
        self.assertEquals(raw_input('?'), 'a')
        self.assertEquals(raw_input('?'), '1234')
        self.assertEquals(raw_input('?'), '1 2 3')
        self.assertRaises(IndexError, raw_input, '?')
            
        raw_input = MockRawInput(1)
        self.assertRaises(TypeError, raw_input, '?')                
        
    def testGetInputWithDefaultWithStrings(self):
        diffcalc.utils.raw_input = MockRawInput('reply')
        print">>>"
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), 'reply')
        print">>>"
        diffcalc.utils.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), 'default')
        print">>>"
        diffcalc.utils.raw_input = MockRawInput('1.23 1 a')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), '1.23 1 a')

    def testGetInputWithDefaultWithNumbers(self):
        diffcalc.utils.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', 1), 1.0)
        
        diffcalc.utils.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', 1.23), 1.23)                
                        
        diffcalc.utils.raw_input = MockRawInput('1')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), 1.0)
        
        diffcalc.utils.raw_input = MockRawInput('1.23')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), 1.23)        

    def testGetInputWithDefaultWithLists(self):
        diffcalc.utils.raw_input = MockRawInput('')
        self.assertEquals(getInputWithDefault('enter a thing', (1, 2.0, 3.1)), (1.0, 2.0, 3.1))
        
        diffcalc.utils.raw_input = MockRawInput('1 2.0 3.1')
        self.assertEquals(getInputWithDefault('enter a thing', 'default'), [1.0, 2.0, 3.1])
    
    def testDiffer(self):
        self.assertEquals(differ([1., 2., 3.], [1., 2., 3.], .000000000000000001), False)
        self.assertEquals(differ(1, 1.0, .000000000000000001), False)
        self.assertEquals(differ([2., 4., 6.], [1., 2., 3.], .1) , '(2.0, 4.0, 6.0)!=(1.0, 2.0, 3.0)')
        
        self.assertEquals(differ(1., 1.2, .2), False)
        self.assertEquals(differ(1., 1.2, .1999999999999), '1.0!=1.2')
        self.assertEquals(differ(1., 1.2, 1.20000000000001), False)

    def testNearlyEqual(self):
        self.assertEquals(nearlyEqual([1, 2, 3], [1, 2, 3], .000000000000000001), True)
        self.assertEquals(nearlyEqual(1, 1.0, .000000000000000001), True)
        self.assertEquals(nearlyEqual([2, 4, 6], [1, 2, 3], .1) , False)
        
        self.assertEquals(nearlyEqual(1, 1.2, .2), True)
        self.assertEquals(nearlyEqual(1, 1.2, .1999999999999), False)
        self.assertEquals(nearlyEqual(1, 1.2, 1.20000000000001), True)

    def testDegreesEqual(self):
        tol = .001
        self.assertEquals(degreesEquivilant(1, 1, tol), True)
        self.assertEquals(degreesEquivilant(1, -359, tol), True)
        self.assertEquals(degreesEquivilant(359, -1, tol), True)
        self.assertEquals(degreesEquivilant(1.1, 1, tol), False)
        self.assertEquals(degreesEquivilant(1.1, -359, tol), False)
        self.assertEquals(degreesEquivilant(359.1, -1, tol), False)


class TestPosition(unittest.TestCase):

    def testCompare(self):
        # Test the compare method
        pos1 = VliegPosition(1, 2, 3, 4, 5, 6)
        pos2 = VliegPosition(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
        
        self.assert_(pos1 == pos1)
        self.assert_(pos1 != pos2)

    def testNearlyEquals(self):
        pos1 = VliegPosition(1, 2, 3, 4, 5, 6)
        pos2 = VliegPosition(1.1, 2.1, 3.1, 4.1, 5.1, 6.1)
        self.assert_(pos1.nearlyEquals(pos2, 0.3))
        self.assert_(not pos1.nearlyEquals(pos2, 0.2))
        
    def testClone(self):
        pos = VliegPosition(1, 2, 3, 4., 5., 6.)
        copy = pos.clone()
        self.assert_(pos == copy)
        pos.alpha = 10
        pos.omega = 4.1
        
