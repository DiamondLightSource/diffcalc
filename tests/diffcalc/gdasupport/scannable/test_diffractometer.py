from mock import Mock
from diffcalc.gdasupport.scannable.slave_driver import SlaveScannableDriver
try:
    from gda.device.scannable.scannablegroup import ScannableGroup
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.group import ScannableGroup

from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.mock import MockMotor
from tests.diffcalc.gdasupport.scannable.mockdiffcalc import MockDiffcalc
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

class MockSlaveScannableDriver(object):
    
    def __init__(self):
        self.busy = False
        self.lastPosition = None
    
    def isBusy(self):
        return self.busy
    
    def triggerAsynchronousMove(self, position):
        self.lastPosition = position
        
    def getPositions(self):
        return 90, 91


class TestDiffractometerScannableGroup(unittest.TestCase):
    
    def setUp(self):
        self.a = MockMotor()
        self.b = MockMotor()
        self.c = MockMotor()
        self.d = MockMotor()
        self.e = MockMotor()
        self.f = MockMotor()#
        self.grp = ScannableGroup('grp', [self.a, self.b, self.c, self.d, self.e, self.f])
        self.grp.configure()
        self.sg = DiffractometerScannableGroup('sixc', MockDiffcalc(6), self.grp)
    
    def testInit(self):
        self.assertEqual(list(self.sg.getPosition()), [0.0 , 0.0 , 0.0, 0.0 , 0.0 , 0.0])
    
    def testAsynchronousMoveTo(self):
        self.sg.asynchronousMoveTo([1, 2.0, 3, 4, 5, 6])
        self.assertEqual(list(self.sg.getPosition()), [1.0 , 2.0 , 3.0, 4.0, 5.0, 6.0])
    
    def testAsynchronousMoveToWithNones(self):
        self.sg.asynchronousMoveTo([1.0, 2.0 , 3.0, 4.0, 5.0, 6.0])
        self.sg.asynchronousMoveTo([None, None, 3.2, None, 5.2, None])
        self.assertEqual(list(self.sg.getPosition()), [1.0 , 2.0 , 3.2, 4.0, 5.2, 6.0])

    def testGetPosition(self):
        #implicitely tested above
        pass
    
    def testWhereMoveTo(self):
        # just check for exceptions
        print self.sg.simulateMoveTo((1.23, 2, 3, 4, 5, 6))

    def testIsBusy(self):    
        self.assertEqual(self.sg.isBusy(), False)
        self.sg.asynchronousMoveTo([1.0, 2.0 , 3.0, 4, 5, 6])
        self.assertEqual(self.sg.isBusy(), True)
        self.b.makeNotBusy()
        self.assertEqual(self.sg.isBusy(), True)
        self.a.makeNotBusy()    
        self.c.makeNotBusy()    
        self.d.makeNotBusy()    
        self.e.makeNotBusy()
        self.f.makeNotBusy()    
        self.assertEqual(self.sg.isBusy(), False)
    
    def testRepr(self):
        print self.sg.__repr__()


class TestDiffractometerScannableGroupWithSlave(TestDiffractometerScannableGroup):

    def setUp(self):
        TestDiffractometerScannableGroup.setUp(self)
        self.mock_driver = Mock(spec=SlaveScannableDriver)
        self.mock_driver.getPositions.return_value = 90, 91
        self.mock_driver.isBusy.return_value = False
        self.mock_driver.getScannableNames.return_value = 'a', 'b'

        self.sg.slave_driver = self.mock_driver
    
    def test__init__(self):
        sg = DiffractometerScannableGroup('sixc', MockDiffcalc(6), self.grp, self.mock_driver)
        self.assertEquals(sg.slave_driver, self.mock_driver)
        
    def testAsynchronousMoveToWithNones(self):
        self.sg.asynchronousMoveTo([1.0, 2.0 , 3.0, 4.0, 5.0, 6.0])
        self.sg.asynchronousMoveTo([None, None, 3.2, None, 5.2, None])
        self.assertEqual(list(self.sg.getPosition()), [1.0 , 2.0 , 3.2, 4.0, 5.2, 6.0, 90, 91])
        self.mock_driver.triggerAsynchronousMove.assert_called_with(
                                                [None, None, 3.2, None, 5.2, None])

    def testIsBusyWithSlave(self):    
        self.mock_driver.isBusy.return_value = True
        self.assertEqual(self.sg.isBusy(), True)
    
    ### overridden
        
    def testInit(self):
        self.assertEqual(list(self.sg.getPosition()), [0.0 , 0.0 , 0.0, 0.0 , 0.0 , 0.0, 90, 91])
    
    def testAsynchronousMoveTo(self):
        self.sg.asynchronousMoveTo([1, 2.0, 3, 4, 5, 6])
        self.assertEqual(list(self.sg.getPosition()), [1.0 , 2.0 , 3.0, 4.0, 5.0, 6.0, 90, 91])
    

class TestDiffractometerScannableGroupWithFailingAngleCalculator(unittest.TestCase):

    def setUp(self):
        class BadMockAngleCalculator:    
            def _anglesToHkl(self, pos):
                raise Exception("Problem")
        self.group = ScannableGroup('grp', createDummyAxes(['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi']))
        self.group.configure()
        self.sg = DiffractometerScannableGroup('sixc', BadMockAngleCalculator(), self.group)

    def testGetPosition(self):
        self.sg.getPosition()
        
    def testSimulateMoveTo(self):
        self.assertEqual(self.sg.simulateMoveTo([1.0, 2.0 , 3.0, 4.0, 5.0, 6.0]), "Error: Problem")
