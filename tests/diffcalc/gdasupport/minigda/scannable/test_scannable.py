from diffcalc.gdasupport.minigda.scannable.dummy import \
    SingleFieldDummyScannable
from diffcalc.gdasupport.minigda.scannable.scannable import Scannable
import unittest


class TestScannable(unittest.TestCase):
    
    def setUp(self):
        self.scannable = Scannable()

    def testSomethingUnrelated(self):
        a = SingleFieldDummyScannable('a')
        print isinstance(a, Scannable)

