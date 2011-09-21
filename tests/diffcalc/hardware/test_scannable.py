from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.mock import MockMotor
from diffcalc.hardware.scannable import ScannableHardwareMonitorPlugin
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

class TestGdaHardwareMonitor(unittest.TestCase):
    
    def setUp(self):
        self.grp = ScannableGroup('grp', createDummyAxes(['a', 'b', 'c', 'd', 'e', 'f']))
        self.diffhw = DiffractometerScannableGroup('sixc', MockDiffcalc(6), self.grp)
        self.energyhw = MockMotor()
        self.hardware = ScannableHardwareMonitorPlugin(self.diffhw, self.energyhw)

    def test__init__AndGetPhysicalAngleNames(self):
        self.assertEquals(self.hardware.getPhysicalAngleNames(), ('a', 'b', 'c', 'd', 'e', 'f'))

    def testGetPosition(self):
        self.diffhw.asynchronousMoveTo((1, 2, 3, 4, 5, 6))
        self.assertEqual(self.hardware.getPosition(), [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def testGetEnergy(self):
        self.energyhw.asynchronousMoveTo(1.0)
        self.assertEqual(self.hardware.getEnergy(), 1.0)
        
    def testGetWavelength(self):
        self.energyhw.asynchronousMoveTo(1.0)
        self.assertEqual(self.hardware.getWavelength(), 12.39842 / 1.0)
