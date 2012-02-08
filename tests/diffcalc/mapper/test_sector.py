
from diffcalc.mapper.sector import VliegSectorSelector, TransformA, TransformB, \
    TransformC, transformsFromSector
from diffcalc.hkl.vlieg.position  import VliegPosition as P
from mock import Mock
import unittest
# self.alpha, self.delta, self.gamma, self.omega, self.chi, self.phi

class MockLimitChecker(object):
    
    def __init__(self):
        self.okay = True
        
    def isPoswithiLimits(self, pos):
        return self.okay
    
    def isDeltaNegative(self, pos):
        return pos.delta <= 0


class TestSectorSelector(unittest.TestCase):
    
    def setUp(self):
        self.limitChecker = MockLimitChecker()
        self.ss = VliegSectorSelector()
        self.ss.limitCheckerFunction = self.limitChecker.isPoswithiLimits
    
    def test__init__(self):
        self.assertEquals(self.ss.sector, 0)
    
    def testCutPosition(self):
        d = .1
        self.assert_(self.ss.cutPosition(P(-180., 180., 180. - d, 180. + d, -180. + d, -180. - d)) == P(-180., 180., 180. - d, -180. + d, -180. + d, 180. - d))

    def testTransformNWithoutCut(self):
        pos = P(1, 2, 3, 4, 5, 6)
        self.assert_(self.ss.transformNWithoutCut(0, pos) == pos)

    def testTransformPosition(self):
        pos = P(0 - 360, .1 + 360, .2 - 360, .3 + 360, .4, 5)
        res = self.ss.transformPosition(pos)
        des = P(0, .1, .2, .3, .4, 5)
        self.assert_(res == des, '%s!=\n%s' % (res, des))

    def testSetSector(self):
        self.ss.setSector(4)
        self.assertEquals(self.ss.sector, 4)
        self.assertEquals(self.ss.transforms, ['b', 'c'])

    def testSetTransforms(self):
        self.ss.setTransforms(('c', 'b'))
        self.assertEquals(self.ss.sector, 4)
        self.assertEquals(self.ss.transforms, ['b', 'c'])

    def testAddAutoTransormWithBadInput(self):
        self.assertEquals(self.ss.autosectors, [])
        self.assertEquals(self.ss.autotransforms, [])
        self.assertRaises(ValueError, self.ss.addAutoTransorm, 'not a transform letter')
        self.assertRaises(ValueError, self.ss.addAutoTransorm, 9999)
        self.assertRaises(ValueError, self.ss.addAutoTransorm, [])

    def testAddAutoTransormWithTransforms(self):
        self.ss.autosectors = [1, 2, 3, 4, 5]
        self.ss.addAutoTransorm('a')
        print "Should now print a warning..."
        self.ss.addAutoTransorm('a') # twice
        self.ss.addAutoTransorm('b')
        self.assertEquals(self.ss.autosectors, [])
        self.assertEquals(self.ss.autotransforms, ['a', 'b'])

    def testAddAutoTransormWithSectors(self):
        self.ss.autotransforms = ['a', 'c']
        self.ss.addAutoTransorm(2)
        print "Should now print a warning..."
        self.ss.addAutoTransorm(2) # twice
        self.ss.addAutoTransorm(3)
        self.assertEquals(self.ss.autosectors, [2, 3])
        self.assertEquals(self.ss.autotransforms, [])

    def testIsPositionWithinLimits(self):
        self.assertEquals(self.ss.isPositionWithinLimits(None), True)
        self.limitChecker.okay = False
        self.assertEquals(self.ss.isPositionWithinLimits(None), False)

    def test__repr__(self):
        self.ss.setSector(0)
        print "************************"
        print self.ss
        print "************************"
        self.ss.setTransforms('a')
        print self.ss
        print "************************"
        self.ss.setTransforms(('a', 'b', 'c'))
        print self.ss
        print "************************"


class TestSectorSelectorAutoCode(unittest.TestCase):
    
    def setUp(self):
        self.limitChecker = MockLimitChecker()
        self.ss = VliegSectorSelector()
        self.ss.limitCheckerFunction = self.limitChecker.isDeltaNegative
        self.pos = P(0, .1, .2, .3, .4, 5)
        self.pos_in2 = self.ss.cutPosition(self.ss.transformNWithoutCut(2, self.pos))
        self.pos_in3 = self.ss.cutPosition(self.ss.transformNWithoutCut(3, self.pos))

    def testAddautoTransformWithSectors(self):
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        self.assertEquals(self.ss.autosectors, [2, 3])
        self.assertEquals(self.ss.autotransforms, [])
        self.ss.removeAutoTransform(3)
        self.assertEquals(self.ss.autosectors, [2])
        
    def testAddautoTransformTransforms(self):
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('b')
        self.assertEquals(self.ss.autosectors, [])
        self.assertEquals(self.ss.autotransforms, ['a', 'b'])

    def testRemoveAutoTransformWithSectors(self):
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        self.ss.removeAutoTransform(3)
        self.assertEquals(self.ss.autosectors, [2])
        self.ss.removeAutoTransform(2)
        self.assertEquals(self.ss.autosectors, [])
        
    def testRemoveAutoTransformTransforms(self):
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('b')
        self.ss.removeAutoTransform('b')
        self.assertEquals(self.ss.autotransforms, ['a'])
        self.ss.removeAutoTransform('a')
        self.assertEquals(self.ss.autotransforms, [])

    def testTransformPosition(self):
        # Check that with no transforms set to autoapply, the limit
        # checker function is ignored
        ss = VliegSectorSelector()
        ss.limitCheckerFunction = self.limitChecker.isPoswithiLimits
        self.limitChecker.okay = False
        ss.transformPosition(P(0, .1, .2, .3, .4, 5))

    def testMockLimitChecker(self):
        self.assertEquals(self.limitChecker.isDeltaNegative(P(0, .1, .2, .3, .4, 5)), False)
        self.assertEquals(self.limitChecker.isDeltaNegative(P(0, -.1, .2, .3, .4, 5)), True)
        
    def testAutoTransformPositionWithSectors(self):
        self.ss.addAutoTransorm(2)
        print "Should print 'INFO: Autosector changed sector from 0 to 2':"
        self.assert_(self.ss.autoTransformPositionBySector(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
    
    def testAutoTransformPositionWithSectorChoice(self):
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        print "Should print 'WARNING: Autosector found multiple sectors...':"
        print "Should print 'INFO: Autosector changed sector from 0 to 2':"
        self.assert_(self.ss.autoTransformPositionBySector(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testAutoTransformPositionWithSectorsFails(self):
        self.ss.addAutoTransorm(0)
        self.ss.addAutoTransorm(1)
        self.ss.addAutoTransorm(4)
        self.ss.addAutoTransorm(5)
        print "Should print 'INFO: Autosector changed sector from 0 to 2':"
        self.assertRaises(Exception, self.ss.autoTransformPositionBySector, self.pos)
        #self.ss.autoTransformPositionBySector(self.pos)

        self.assertEquals(self.ss.sector, 0) # unchanged

    def testCreateListOfPossibleTransforms(self):
        self.ss.addAutoTransorm('a')
        self.assertEquals(self.ss.createListOfPossibleTransforms(), [(), ['a', ]])
        self.ss.addAutoTransorm('b')
        self.assertEquals(self.ss.createListOfPossibleTransforms(), [(), ['b', ], ['a', ], ['a', 'b']])
        self.ss.transforms = ['a', 'c']
        
        
    def testAutoTransformPositionWithTransforms(self):
        self.ss.addAutoTransorm('a')
        print "Should print 'INFO: ':"
        self.assert_(self.ss.autoTransformPositionByTransforms(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
    
    def testAutoTransformPositionWithTansformsChoice(self):
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('c')
        print "Should print 'WARNING:':"
        print "Should print 'INFO: ':"
        self.assert_(self.ss.autoTransformPositionByTransforms(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testTransformPositionWithAutoTransforms(self):
        self.ss.addAutoTransorm('a')
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
        print "Should not print 'INFO...'" #
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
        
    def testTransformPositionWithAutoTransforms2(self):
        self.ss.addAutoTransorm(2)
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
        print "Should not print 'INFO...'" #
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)        
    
    def test__repr__(self):
        self.ss.setSector(0)
        print "************************"
        print self.ss
        print "************************"
        self.ss.setTransforms('a')
        print self.ss
        print "************************"
        self.ss.setTransforms(('a', 'b', 'c'))
        print self.ss
        print "************************"
        
        self.ss.addAutoTransorm(1)
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        print self.ss
        print "************************"
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('c')
        print self.ss
        print "************************"




class TestTransforms(unittest.TestCase):
    
    def setUp(self):
        self.limitCheckerFunction = Mock()
        self.ss = VliegSectorSelector()
        self.ss.limitCheckerFunction = self.limitCheckerFunction
        
    def applyTransforms(self, transforms, pos):
        result = pos.clone()
        for transform in transforms:
            if transform == 'a':
                result = TransformA().transform(result)
            if transform == 'b':
                result = TransformB().transform(result)
            if transform == 'c':
                result = TransformC().transform(result)
        return self.ss.cutPosition(result)
    
    def _testTransformN(self, n):
        transforms = transformsFromSector[n]
        pos = P(1, 2, 3, 4, 5, 6)
        self.ss.setSector(n)
        fromss = self.ss.transformPosition(pos)
        fromhere = self.applyTransforms(transforms, pos)
        self.assert_(fromss == fromhere, "sector: %i\ntransforms:%s\n%s !=\n%s" % (n, transforms, fromss, fromhere))

    def testTransform0(self):
        self._testTransformN(0)
            
    def testTransform1(self):
        self._testTransformN(1)

    def testTransform2(self):
        self._testTransformN(2)
            
    def testTransform3(self):
        self._testTransformN(3)

    def testTransform4(self):
        self._testTransformN(5)
            
    def testTransform5(self):
        self._testTransformN(5)

    def testTransform6(self):
        self._testTransformN(6)
            
    def testTransform7(self):
        self._testTransformN(7)
