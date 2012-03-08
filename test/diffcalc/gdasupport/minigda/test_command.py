###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

import unittest

from diffcalc.gdasupport.minigda.command import Pos, Scan, ScanDataPrinter
from diffcalc.gdasupport.minigda.scannable import \
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
        result = [r[0].scannable, r[0].args, r[1].scannable, r[1].args,
                  r[2].scannable, r[2].args, r[3].scannable, r[3].args]
        desired = [scnA, [1, 2, 3], scnB, [[4, 5, 6], ], scnC, list(), scnD,
                   [1.123456]]
        self.assertEqual(result, desired)

    def test__reorderGroupsAccordingToLevel(self):
        scn4 = SingleFieldDummyScannable('scn4')
        scn4.setLevel(4)
        scn5a = SingleFieldDummyScannable('scn5a')
        scn5a.setLevel(5)
        scn5b = SingleFieldDummyScannable('scn5b')
        scn5b.setLevel(5)
        scn6 = SingleFieldDummyScannable('scn6')
        scn6.setLevel(6)

        def t(scanargs):
            groups = self.scan._parseScanArgsIntoScannableArgGroups(scanargs)
            r = self.scan._reorderInnerGroupsAccordingToLevel(groups)
            return [r[0].scannable, r[1].scannable, r[2].scannable,
                    r[3].scannable]

        self.assertEqual(t((scn5a, 1, 2, 3, scn6, 1, scn5b, scn4)),
                         [scn5a, scn4, scn5b, scn6])
        self.assertEqual(t((scn5a, 1, 3, scn6, 1, scn5b, scn4)),
                         [scn4, scn5a, scn5b, scn6])

    def test__Frange(self):
        self.assertEquals(self.scan._frange(1, 1.3, .1), [1.0, 1.1, 1.2, 1.3])

    def test__Call__(self):
        scn4 = SingleFieldDummyScannable('scn4')
        scn4.setLevel(4)
        scn5a = SingleFieldDummyScannable('scn5a')
        scn5a.setLevel(5)
        scn5b = SingleFieldDummyScannable('scn5b')
        scn5b.setLevel(5)
        scn6 = SingleFieldDummyScannable('scn6')
        scn6.setLevel(6)
        self.scan.__call__(scn5a, 1, 3, 1, scn6, 1, scn5b, scn4)
