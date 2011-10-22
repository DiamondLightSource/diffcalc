from diffcalc.gdasupport.minigda.commands.scan import Scan, ScanDataPrinter
from diffcalc.gdasupport.minigda.scannable.dummy import \
    SingleFieldDummyScannable
import unittest

class TestScan(unittest.TestCase):
    def setUp(self):
        self.scan = Scan([ScanDataPrinter()])
        
    def test__parseScanArgsIntoScannableArgGroups(self):
        scnA = SingleFieldDummyScannable('scnA')
        scnB = SingleFieldDummyScannable('scnB')
        scnC = SingleFieldDummyScannable('scnC')
        scnD = SingleFieldDummyScannable('scnD')

        scanargs = (scnA, 1, 2, 3, scnB, [4, 5, 6], scnC, scnD, 1.123456)
        r = self.scan._parseScanArgsIntoScannableArgGroups(scanargs)
        result = [ r[0].scannable, r[0].args, r[1].scannable, r[1].args, r[2].scannable, r[2].args, r[3].scannable, r[3].args ]
        desired = [ scnA, [1, 2, 3], scnB, [[4, 5, 6], ], scnC, list(), scnD, [1.123456]]
        self.assertEqual(result, desired)
        
    def test__reorderGroupsAccordingToLevel(self):    
        scn4 = SingleFieldDummyScannable('scn4');scn4.setLevel(4)
        scn5a = SingleFieldDummyScannable('scn5a');scn5a.setLevel(5)
        scn5b = SingleFieldDummyScannable('scn5b');scn5b.setLevel(5)
        scn6 = SingleFieldDummyScannable('scn6');scn6.setLevel(6)    

        def t(scanargs):
            groups = self.scan._parseScanArgsIntoScannableArgGroups(scanargs)
            r = self.scan._reorderInnerGroupsAccordingToLevel(groups)
            return [r[0].scannable, r[1].scannable, r[2].scannable, r[3].scannable]
        
        self.assertEqual(t((scn5a, 1, 2, 3, scn6, 1, scn5b, scn4)), [scn5a, scn4, scn5b, scn6])
        self.assertEqual(t((scn5a, 1, 3, scn6, 1, scn5b, scn4)), [scn4, scn5a, scn5b, scn6])
        
    def test__Frange(self):
        self.assertEquals(self.scan._frange(1, 1.3, .1), [1.0, 1.1, 1.2, 1.3])

    def test__Call__(self):
        scn4 = SingleFieldDummyScannable('scn4');scn4.setLevel(4)
        scn5a = SingleFieldDummyScannable('scn5a');scn5a.setLevel(5)
        scn5b = SingleFieldDummyScannable('scn5b');scn5b.setLevel(5)
        scn6 = SingleFieldDummyScannable('scn6');scn6.setLevel(6)
        self.scan.__call__(scn5a, 1, 3, 1, scn6, 1, scn5b, scn4)
