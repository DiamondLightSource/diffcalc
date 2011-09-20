from diffcalc.gdasupport.scannable.wavelength import Wavelength
try:
    from gdascripts.pd.dummy_pds import DummyPD
except ImportError:
    print "WARNING: ExampleSixCircleStartup.py is not running within the GDA: falling back to the (very minimal!) minigda..."
    from diffcalc.gdasupport.minigda.scannable.dummy import DummyPD
import unittest

class TestWavelength(unittest.TestCase):
    
    def setUp(self):
        self.en = DummyPD('en')
        self.wl = Wavelength('wl', self.en)

    def testIt(self):
        self.en.asynchronousMoveTo(12.39842)
        self.assertEqual(self.wl.getPosition(),1)
        
        self.wl.asynchronousMoveTo(1.)
        self.assertEqual(self.wl.getPosition(), 1.)
        self.assertEqual(self.en.getPosition(), 12.39842)
