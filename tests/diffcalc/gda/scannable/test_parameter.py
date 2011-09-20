from tests.diffcalc.gda.scannable.mockdiffcalc import MockDiffcalc
from diffcalc.gdasupport.scannable.parameter import DiffractionCalculatorParameter
import unittest


class TestDiffractionCalculatorParameter(unittest.TestCase):
    
    def setUp(self):
        self.dcp = DiffractionCalculatorParameter('dcp', 'betain' , MockDiffcalc(6) )
        
    def testAsynchronousMoveToAndGetPosition(self):
        self.dcp.asynchronousMoveTo(12.3)
        self.assertEqual(self.dcp.getPosition(),12.3)

    def testIsBusy(self):
        self.assertEqual(self.dcp.isBusy(),False)
