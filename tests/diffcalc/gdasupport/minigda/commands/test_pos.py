import unittest

from diffcalc.gdasupport.minigda.commands.pos import Pos
from diffcalc.gdasupport.minigda.scannable.dummy import \
    MultiInputExtraFieldsDummyScannable, SingleFieldDummyScannable


class BadSingleFieldDummyScannable(SingleFieldDummyScannable):
        def getPosition(self):
            raise Exception("Problem")


class NoneReturningSingleFieldDummyScannable(SingleFieldDummyScannable):
        def getPosition(self):
            return None


class TestPos(unittest.TestCase):

    def setUp(self):
        self.dummyMainNamespace = namespace = {}
        namespace['notAScannable'] = 3.124
        namespace['scnA'] = SingleFieldDummyScannable('scnA')
        namespace['scnB'] = SingleFieldDummyScannable('scnB')
        namespace['scnC'] = SingleFieldDummyScannable('scnC')
        namespace['scnD'] = SingleFieldDummyScannable('scnD')
        namespace['scnNone'] = \
            NoneReturningSingleFieldDummyScannable('scnNone')
        namespace['scnBad'] = BadSingleFieldDummyScannable('scnBad')
        self.pos = Pos(self.dummyMainNamespace)

    def testPosReturningReportWithRead(self):
        scnA = self.dummyMainNamespace['scnA']
        self.assertEquals(self.pos.posReturningReport(scnA),
                          'scnA:     0.0000')

    def testPosReturningReportWithMove(self):
        scnA = self.dummyMainNamespace['scnA']
        self.assertEquals(self.pos.posReturningReport(scnA, 1.123),
                          'scnA:     1.1230')

    def test__call__(self):
        scnA = self.dummyMainNamespace['scnA']
        self.pos.__call__(scnA)
        self.pos.__call__(scnA, 4.321)
        print "*"
        self.pos.__call__()
        print "*"

    def testPosReturningReportWithMultiFieldScannables(self):
        scn = MultiInputExtraFieldsDummyScannable('mie', ['i1', 'i2'], ['e1'])
        self.assertEquals(self.pos.posReturningReport(scn),
                          'mie:      i1: 0.0000 i2: 0.0000 e1: 100.0000 ')

    def testPosReturningReportWithBadScannable(self):
        scnBad = self.dummyMainNamespace['scnBad']
        self.assertEquals(self.pos.posReturningReport(scnBad),
                          "scnBad:   Error: Problem")
        self.assertEquals(self.pos.posReturningReport(scnBad, 4.321),
                          "scnBad:   Error: Problem")

    def testPosReturningReportWithNoneReturningScannable(self):
        scnNone = self.dummyMainNamespace['scnNone']
        self.assertEquals(self.pos.posReturningReport(scnNone),
                          "scnNone:  ---")
        self.assertEquals(self.pos.posReturningReport(scnNone, 4.321),
                          "scnNone:  ---")
