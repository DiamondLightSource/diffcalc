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

from nose.tools import eq_
import unittest

from mock import Mock

from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hkl.vlieg.geometry import VliegPosition as P, \
   VliegPosition as Pos
from diffcalc.hkl.vlieg.transform import TransformA, TransformB, TransformC, \
    transformsFromSector, TransformCommands, \
    VliegTransformSelector, VliegPositionTransformer
import diffcalc.util  # @UnusedImport


class TestVliegPositionTransformer(unittest.TestCase):

    def setUp(self):
        names = 'a', 'd', 'g', 'o', 'c', 'phi'
        self.hardware = DummyHardwareAdapter(names)
        self.geometry = SixCircleGammaOnArmGeometry()

        self.transform_selector = VliegTransformSelector()
        self.transformer = VliegPositionTransformer(
            self.geometry, self.hardware, self.transform_selector)
        self.transform_commands = TransformCommands(self.transform_selector)

        diffcalc.util.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True

    def map(self, pos):  # @ReservedAssignment
        pos = self.transformer.transform(pos)
        angle_tuple = self.geometry.internal_position_to_physical_angles(pos)
        angle_tuple = self.hardware.cut_angles(angle_tuple)
        return angle_tuple

    def testMapDefaultSector(self):

        eq_(self.map(Pos(1, 2, 3, 4, 5, 6)),
            (1, 2, 3, 4, 5, 6))

        eq_(self.map(Pos(-180, -179, 0, 179, 180, 359)),
            (-180, -179, 0, 179, 180, 359))

        eq_(self.map(Pos(0, 0, 0, 0, 0, 0)),
            (0, 0, 0, 0, 0, 0))

        eq_(self.map(Pos(-270, 270, 0, 0, 0, -90)),
            (90, -90, 0, 0, 0, 270))

    def testMapSector1(self):
        self.transform_commands._sectorSelector.setSector(1)

        eq_(self.map(Pos(1, 2, 3, 4, 5, 6)),
            (1, 2, 3, 4 - 180, -5, (6 - 180) + 360))

        eq_(self.map(Pos(-180, -179, 0, 179, 180, 359)),
            (-180, -179, 0, 179 - 180, -180, 359 - 180))

        eq_(self.map(Pos(0, 0, 0, 0, 0, 0)),
            (0, 0, 0, 0 - 180, 0, (0 - 180) + 360))

        eq_(self.map(Pos(-270, 270, 0, 0, 0, -90)),
            (90, -90, 0, 0 - 180, 0, 270 - 180))

    def testMapAutoSector(self):
        self.transform_commands._sectorSelector.addAutoTransorm(1)
        self.hardware.set_lower_limit('c', 0)

        eq_(self.map(Pos(1, 2, 3, 4, -5, 6)),
            (1, 2, 3, 4 - 180, 5, (6 - 180) + 360))

        eq_(self.map(Pos(-180, -179, 0, 179, -180, 359)),
            (-180, -179, 0, 179 - 180, 180, 359 - 180))

        eq_(self.map(Pos(0, 0, 0, 0, -5, 0)),
            (0, 0, 0, 0 - 180, 5, (0 - 180) + 360))

        eq_(self.map(Pos(-270, 270, 0, 0, -5, -90)),
            (90, -90, 0, 0 - 180, 5, 270 - 180))

    def testTransform(self):
        # mapper
        self.transform_commands.transform()  # should print its state
        self.assertRaises(TypeError, self.transform_commands.transform, 1)
        self.assertRaises(TypeError, self.transform_commands.transform, 'a', 1)

    def testTransformsOnOff(self):
        # transforma [on/off/auto/manual]
        ss = self.transform_commands._sectorSelector
        self.transform_commands.transforma()  # should print mapper state
        eq_(ss.transforms, [], "test assumes transforms are off to start")
        self.transform_commands.transforma('on')
        eq_(ss.transforms, ['a'])
        self.transform_commands.transformb('on')
        eq_(ss.transforms, ['a', 'b'])
        self.transform_commands.transformc('off')
        eq_(ss.transforms, ['a', 'b'])
        self.transform_commands.transformb('off')
        eq_(ss.transforms, ['a'])

    def testTransformsAuto(self):
        ss = self.transform_commands._sectorSelector
        eq_(ss.autotransforms, [], "test assumes transforms are off to start")
        self.transform_commands.transforma('auto')
        eq_(ss.autotransforms, ['a'])
        self.transform_commands.transformb('auto')
        eq_(ss.autotransforms, ['a', 'b'])
        self.transform_commands.transformc('manual')
        eq_(ss.autotransforms, ['a', 'b'])
        self.transform_commands.transformb('manual')
        eq_(ss.autotransforms, ['a'])

    def testTransformsBadInput(self):
        transforma = self.transform_commands.transforma
        self.assertRaises(TypeError, transforma, 1)
        self.assertRaises(TypeError, transforma, 'not_valid')
        self.assertRaises(TypeError, transforma, 'auto', 1)

    def testSector(self):
        #sector [0-7]
        ss = self.transform_commands._sectorSelector
        self.transform_commands.sector()  # should print mapper state
        eq_(ss.sector, 0, "test assumes sector is 0 to start")
        self.transform_commands.sector(1)
        eq_(ss.sector, 1)
        self.assertRaises(TypeError, self.transform_commands.sector, 1, 2)
        self.assertRaises(TypeError, self.transform_commands.sector, 'a')

    def testAutosectors(self):
        #autosector [0-7]
        ss = self.transform_selector
        self.transform_commands.autosector()  # should print mapper state
        eq_(ss.autosectors, [], "test assumes no auto sectors to start")
        self.transform_commands.autosector(1)
        eq_(ss.autosectors, [1])
        self.transform_commands.autosector(1, 2)
        eq_(ss.autosectors, [1, 2])
        self.transform_commands.autosector(1)
        eq_(ss.autosectors, [1])
        self.transform_commands.autosector(3)
        eq_(ss.autosectors, [3])
        self.assertRaises(
            TypeError, self.transform_commands.autosector, 1, 'a')
        self.assertRaises(
            TypeError, self.transform_commands.autosector, 'a')


class MockLimitChecker(object):

    def __init__(self):
        self.okay = True

    def isPoswithiLimits(self, pos):
        return self.okay

    def isDeltaNegative(self, pos):
        return pos.delta <= 0


class TestVliegTransformSelector(unittest.TestCase):

    def setUp(self):
        self.limitChecker = MockLimitChecker()
        self.ss = VliegTransformSelector()
        self.ss.limitCheckerFunction = self.limitChecker.isPoswithiLimits

    def test__init__(self):
        self.assertEquals(self.ss.sector, 0)

    def testCutPosition(self):
        d = .1
        tocut = P(-180., 180., 180. - d, 180. + d, -180. + d, -180. - d)
        expected = P(-180., 180., 180. - d, -180. + d, -180. + d, 180. - d)
        self.assert_(self.ss.cutPosition(tocut) == expected)

    def testTransformNWithoutCut(self):
        pos = P(1, 2, 3, 4, 5, 6)
        self.assert_(self.ss.transformNWithoutCut(0, pos) == pos)

    def testTransformPosition(self):
        pos = P(0 - 360, .1 + 360, .2 - 360, .3 + 360, .4, 5)
        res = self.ss.transformPosition(pos)
        des = P(0, .1, .2, .3, .4, 5)
        self.assert_(res == des, '%s!=\n%s' % (res, des))

    def testSetSector(self):
        self.ss.setSector(4)
        self.assertEquals(self.ss.sector, 4)
        self.assertEquals(self.ss.transforms, ['b', 'c'])

    def testSetTransforms(self):
        self.ss.setTransforms(('c', 'b'))
        self.assertEquals(self.ss.sector, 4)
        self.assertEquals(self.ss.transforms, ['b', 'c'])

    def testAddAutoTransormWithBadInput(self):
        self.assertEquals(self.ss.autosectors, [])
        self.assertEquals(self.ss.autotransforms, [])
        self.assertRaises(ValueError, self.ss.addAutoTransorm, 'not transform')
        self.assertRaises(ValueError, self.ss.addAutoTransorm, 9999)
        self.assertRaises(ValueError, self.ss.addAutoTransorm, [])

    def testAddAutoTransormWithTransforms(self):
        self.ss.autosectors = [1, 2, 3, 4, 5]
        self.ss.addAutoTransorm('a')
        print "Should now print a warning..."
        self.ss.addAutoTransorm('a')  # twice
        self.ss.addAutoTransorm('b')
        self.assertEquals(self.ss.autosectors, [])
        self.assertEquals(self.ss.autotransforms, ['a', 'b'])

    def testAddAutoTransormWithSectors(self):
        self.ss.autotransforms = ['a', 'c']
        self.ss.addAutoTransorm(2)
        print "Should now print a warning..."
        self.ss.addAutoTransorm(2)  # twice
        self.ss.addAutoTransorm(3)
        self.assertEquals(self.ss.autosectors, [2, 3])
        self.assertEquals(self.ss.autotransforms, [])

    def testis_position_within_limits(self):
        self.assertEquals(self.ss.is_position_within_limits(None), True)
        self.limitChecker.okay = False
        self.assertEquals(self.ss.is_position_within_limits(None), False)

    def test__repr__(self):
        self.ss.setSector(0)
        print "************************"
        print self.ss
        print "************************"
        self.ss.setTransforms('a')
        print self.ss
        print "************************"
        self.ss.setTransforms(('a', 'b', 'c'))
        print self.ss
        print "************************"


class TestSectorSelectorAutoCode(unittest.TestCase):

    def setUp(self):
        self.limitChecker = MockLimitChecker()
        self.ss = VliegTransformSelector()
        self.ss.limitCheckerFunction = self.limitChecker.isDeltaNegative
        self.pos = P(0, .1, .2, .3, .4, 5)
        self.pos_in2 = self.ss.cutPosition(
            self.ss.transformNWithoutCut(2, self.pos))
        self.pos_in3 = self.ss.cutPosition(
            self.ss.transformNWithoutCut(3, self.pos))

    def testAddautoTransformWithSectors(self):
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        self.assertEquals(self.ss.autosectors, [2, 3])
        self.assertEquals(self.ss.autotransforms, [])
        self.ss.removeAutoTransform(3)
        self.assertEquals(self.ss.autosectors, [2])

    def testAddautoTransformTransforms(self):
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('b')
        self.assertEquals(self.ss.autosectors, [])
        self.assertEquals(self.ss.autotransforms, ['a', 'b'])

    def testRemoveAutoTransformWithSectors(self):
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        self.ss.removeAutoTransform(3)
        self.assertEquals(self.ss.autosectors, [2])
        self.ss.removeAutoTransform(2)
        self.assertEquals(self.ss.autosectors, [])

    def testRemoveAutoTransformTransforms(self):
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('b')
        self.ss.removeAutoTransform('b')
        self.assertEquals(self.ss.autotransforms, ['a'])
        self.ss.removeAutoTransform('a')
        self.assertEquals(self.ss.autotransforms, [])

    def testTransformPosition(self):
        # Check that with no transforms set to autoapply, the limit
        # checker function is ignored
        ss = VliegTransformSelector()
        ss.limitCheckerFunction = self.limitChecker.isPoswithiLimits
        self.limitChecker.okay = False
        ss.transformPosition(P(0, .1, .2, .3, .4, 5))

    def testMockLimitChecker(self):
        self.assertFalse(
            self.limitChecker.isDeltaNegative(P(0, .1, .2, .3, .4, 5)))
        self.assertTrue(
            self.limitChecker.isDeltaNegative(P(0, -.1, .2, .3, .4, 5)))

    def testAutoTransformPositionWithSectors(self):
        self.ss.addAutoTransorm(2)
        print "Should print 'INFO: Autosector changed sector from 0 to 2':"
        result = self.ss.autoTransformPositionBySector(self.pos)
        self.assert_(result == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testAutoTransformPositionWithSectorChoice(self):
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        print "Should print 'WARNING: Autosector found multiple sectors...':"
        print "Should print 'INFO: Autosector changed sector from 0 to 2':"
        result = self.ss.autoTransformPositionBySector(self.pos)
        self.assert_(result == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testAutoTransformPositionWithSectorsFails(self):
        self.ss.addAutoTransorm(0)
        self.ss.addAutoTransorm(1)
        self.ss.addAutoTransorm(4)
        self.ss.addAutoTransorm(5)
        print "Should print 'INFO: Autosector changed sector from 0 to 2':"
        self.assertRaises(
            Exception, self.ss.autoTransformPositionBySector, self.pos)
        #self.ss.autoTransformPositionBySector(self.pos)
        self.assertEquals(self.ss.sector, 0)  # unchanged

    def testCreateListOfPossibleTransforms(self):
        self.ss.addAutoTransorm('a')
        self.assertEquals(self.ss.createListOfPossibleTransforms(),
                          [(), ['a', ]])
        self.ss.addAutoTransorm('b')
        self.assertEquals(self.ss.createListOfPossibleTransforms(),
                          [(), ['b', ], ['a', ], ['a', 'b']])
        self.ss.transforms = ['a', 'c']

    def testAutoTransformPositionWithTransforms(self):
        self.ss.addAutoTransorm('a')
        print "Should print 'INFO: ':"
        result = self.ss.autoTransformPositionByTransforms(self.pos)
        self.assert_(result == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testAutoTransformPositionWithTansformsChoice(self):
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('c')
        print "Should print 'WARNING:':"
        print "Should print 'INFO: ':"
        result = self.ss.autoTransformPositionByTransforms(self.pos)
        self.assert_(result == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testTransformPositionWithAutoTransforms(self):
        self.ss.addAutoTransorm('a')
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
        print "Should not print 'INFO...'"
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def testTransformPositionWithAutoTransforms2(self):
        self.ss.addAutoTransorm(2)
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)
        print "Should not print 'INFO...'"
        self.assert_(self.ss.transformPosition(self.pos) == self.pos_in2)
        self.assertEquals(self.ss.sector, 2)

    def test__repr__(self):
        self.ss.setSector(0)
        print "************************"
        print self.ss
        print "************************"
        self.ss.setTransforms('a')
        print self.ss
        print "************************"
        self.ss.setTransforms(('a', 'b', 'c'))
        print self.ss
        print "************************"

        self.ss.addAutoTransorm(1)
        self.ss.addAutoTransorm(2)
        self.ss.addAutoTransorm(3)
        print self.ss
        print "************************"
        self.ss.addAutoTransorm('a')
        self.ss.addAutoTransorm('c')
        print self.ss
        print "************************"


class TestTransforms(unittest.TestCase):

    def setUp(self):
        self.limitCheckerFunction = Mock()
        self.ss = VliegTransformSelector()
        self.ss.limitCheckerFunction = self.limitCheckerFunction

    def applyTransforms(self, transforms, pos):
        result = pos.clone()
        for transform in transforms:
            if transform == 'a':
                result = TransformA().transform(result)
            if transform == 'b':
                result = TransformB().transform(result)
            if transform == 'c':
                result = TransformC().transform(result)
        return self.ss.cutPosition(result)

    def _testTransformN(self, n):
        transforms = transformsFromSector[n]
        pos = P(1, 2, 3, 4, 5, 6)
        self.ss.setSector(n)
        fromss = self.ss.transformPosition(pos)
        fromhere = self.applyTransforms(transforms, pos)
        self.assert_(fromss == fromhere,
                     ("sector: %i\ntransforms:%s\n%s !=\n%s" %
                      (n, transforms, fromss, fromhere)))

    def testTransform0(self):
        self._testTransformN(0)

    def testTransform1(self):
        self._testTransformN(1)

    def testTransform2(self):
        self._testTransformN(2)

    def testTransform3(self):
        self._testTransformN(3)

    def testTransform4(self):
        self._testTransformN(5)

    def testTransform5(self):
        self._testTransformN(5)

    def testTransform6(self):
        self._testTransformN(6)

    def testTransform7(self):
        self._testTransformN(7)
