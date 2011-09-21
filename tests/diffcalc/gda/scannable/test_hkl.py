
from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from tests.diffcalc.gda.scannable.mockdiffcalc import MockDiffcalc
import unittest
try:
    from gdascripts.pd.dummy_pds import DummyPD #@UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD
    
def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result

class TestHkl(unittest.TestCase):
    
    def setUp(self):
        self.group = ScannableGroup('grp', createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi']))
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', MockDiffcalc(6), self.group)
        self.hkl = Hkl('hkl', self.SixCircleGammaOnArmGeometry, MockDiffcalc(6))
        
    def testInit(self):
        self.assertEqual(self.hkl.getPosition(), [0.0 , 0.0 , 0.0])
    
    def testAsynchronousMoveTo(self):
        self.hkl.asynchronousMoveTo([1.123 , 0, 0])
        self.assertEqual(self.SixCircleGammaOnArmGeometry.getPosition(), [1.123, 1.123, 1.123, 1.123, 1.123, 1.123])
    
    def testAsynchronousMoveToWithNones(self):
        self.hkl.asynchronousMoveTo([1.123 , 0, None])
        self.assertEqual(self.SixCircleGammaOnArmGeometry.getPosition(), [1.123, 1.123, 1.123, 1.123, 1.123, 1.123])        
        self.hkl.asynchronousMoveTo([None , 0, None])
        self.assertEqual(self.SixCircleGammaOnArmGeometry.getPosition(), [1.123, 1.123, 1.123, 1.123, 1.123, 1.123])

    def testGetPosition(self):
        self.hkl.asynchronousMoveTo([1.123 , 0, 0])
        self.assertEqual(self.hkl.getPosition(), [1.123, 1.123, 1.123])
    
    def testIsBusy(self):
        self.assertEqual(self.hkl.isBusy(), False)
        
    def testWhereMoveTo(self):
        # just check for exceptions
        print self.hkl.simulateMoveTo((1.23, 0, 0))

    def testDisp(self):
        print self.hkl.__repr__()


class TestHklReturningVirtualangles(TestHkl):
    def setUp(self):
        self.group = ScannableGroup('grp', createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi']))
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', MockDiffcalc(6), self.group)
        self.hkl = Hkl('hkl', self.SixCircleGammaOnArmGeometry, MockDiffcalc(6), ['theta', '2theta', 'Bin', 'Bout', 'azimuth'])

    def testInit(self):
        self.assertEqual(self.hkl.getPosition(), [0.0 , 0.0 , 0.0, 1, 12, 123, 1234, 12345])

    def testGetPosition(self):
        self.hkl.asynchronousMoveTo([1.123 , 0, 0])
        self.assertEqual(self.hkl.getPosition(), [1.123, 1.123, 1.123, 1, 12, 123, 1234, 12345])


class TestHklWithFailingAngleCalculator(unittest.TestCase):
    def setUp(self):
        class BadMockAngleCalculator:    
            def _anglesToHkl(self, pos):
                raise Exception("Problem in _anglesToHkl")
            
        self.group = ScannableGroup('grp', createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi']))
        self.SixCircleGammaOnArmGeometry = DiffractometerScannableGroup('SixCircleGammaOnArmGeometry', MockDiffcalc(6), self.group)
        self.hkl = Hkl('hkl', self.SixCircleGammaOnArmGeometry, BadMockAngleCalculator())

    def testGetPosition(self):
        self.assertRaises(Exception, self.hkl.getPosition, None)

    def test__repr__(self):
        self.assertEqual(self.hkl.__repr__(), "<hkl: Problem in _anglesToHkl>")
        
    def test__str__(self):
        self.assertEqual(self.hkl.__str__() , "<hkl: Problem in _anglesToHkl>")        

    def testComponentGetPosition(self):
        self.assertRaises(Exception, self.hkl.h.getPosition, None)

    def testComponent__repr__(self):
        self.assertEqual(self.hkl.h.__repr__(), "<h: Problem in _anglesToHkl>")
        
    def testComponent__str__(self):
        self.assertEqual(self.hkl.h.__str__() , "<h: Problem in _anglesToHkl>")
