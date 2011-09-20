from diffcalc.gdasupport.minigda.scannable.scannable import Scannable

from diffcalc.gdasupport.minigda.scannable.dummy import SingleFieldDummyScannable
import unittest

class TestScannable(unittest.TestCase):
    def setUp(self):
        self.scannable = Scannable()

    def testSomethingUnrelated(self):
        a= SingleFieldDummyScannable('a')
        print isinstance(a, Scannable)

