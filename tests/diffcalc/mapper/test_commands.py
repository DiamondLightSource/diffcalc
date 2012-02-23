import unittest

import diffcalc.help  # @UnusedImport
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.mapper.commands import MapperCommands
from diffcalc.hkl.vlieg.position  import VliegPosition as Pos
from diffcalc.mapper.sector import VliegSectorSelector
from diffcalc.mapper.mapper import PositionMapper
from nose.tools import eq_


class TestAngleMapper(unittest.TestCase):

    def setUp(self):
        names = 'a', 'd', 'g', 'o', 'c', 'phi'
        self.hardware = DummyHardwareMonitorPlugin(names)
        self.geometry = SixCircleGammaOnArmGeometry()

        self.sector_selector = VliegSectorSelector()
        self.position_mapper = PositionMapper(self.geometry, self.hardware,
                                              self.sector_selector)
        self.mappercommands = MapperCommands(self.geometry, self.hardware,
                                             self.sector_selector)

        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True
        self.map = self.position_mapper.map

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
        self.mappercommands._sectorSelector.setSector(1)

        eq_(self.map(Pos(1, 2, 3, 4, 5, 6)),
            (1, 2, 3, 4 - 180, -5, (6 - 180) + 360))

        eq_(self.map(Pos(-180, -179, 0, 179, 180, 359)),
            (-180, -179, 0, 179 - 180, -180, 359 - 180))

        eq_(self.map(Pos(0, 0, 0, 0, 0, 0)),
            (0, 0, 0, 0 - 180, 0, (0 - 180) + 360))

        eq_(self.map(Pos(-270, 270, 0, 0, 0, -90)),
            (90, -90, 0, 0 - 180, 0, 270 - 180))

    def testMapAutoSector(self):
        self.mappercommands._sectorSelector.addAutoTransorm(1)
        self.hardware.setLowerLimit('c', 0)

        eq_(self.map(Pos(1, 2, 3, 4, -5, 6)),
            (1, 2, 3, 4 - 180, 5, (6 - 180) + 360))

        eq_(self.map(Pos(-180, -179, 0, 179, -180, 359)),
            (-180, -179, 0, 179 - 180, 180, 359 - 180))

        eq_(self.map(Pos(0, 0, 0, 0, -5, 0)),
            (0, 0, 0, 0 - 180, 5, (0 - 180) + 360))

        eq_(self.map(Pos(-270, 270, 0, 0, -5, -90)),
            (90, -90, 0, 0 - 180, 5, 270 - 180))

        self.mappercommands.setmin('phi', -1)
        print "*******"
        self.mappercommands.setmin()
        print "*******"
        self.mappercommands.setmax()
        print "*******"

    def testMapper(self):
        # mapper
        self.mappercommands.mapper()  # should print its state
        self.assertRaises(TypeError, self.mappercommands.mapper, 1)
        self.assertRaises(TypeError, self.mappercommands.mapper, 'a', 1)

    def testTransformsOnOff(self):
        # transforma [on/off/auto/manual]
        ss = self.mappercommands._sectorSelector
        self.mappercommands.transforma()  # should print mapper state
        eq_(ss.transforms, [], "test assumes transforms are off to start")
        self.mappercommands.transforma('on')
        eq_(ss.transforms, ['a'])
        self.mappercommands.transformb('on')
        eq_(ss.transforms, ['a', 'b'])
        self.mappercommands.transformc('off')
        eq_(ss.transforms, ['a', 'b'])
        self.mappercommands.transformb('off')
        eq_(ss.transforms, ['a'])

    def testTransformsAuto(self):
        ss = self.mappercommands._sectorSelector
        eq_(ss.autotransforms, [], "test assumes transforms are off to start")
        self.mappercommands.transforma('auto')
        eq_(ss.autotransforms, ['a'])
        self.mappercommands.transformb('auto')
        eq_(ss.autotransforms, ['a', 'b'])
        self.mappercommands.transformc('manual')
        eq_(ss.autotransforms, ['a', 'b'])
        self.mappercommands.transformb('manual')
        eq_(ss.autotransforms, ['a'])

    def testTransformsBadInput(self):
        transforma = self.mappercommands.transforma
        self.assertRaises(TypeError, transforma, 1)
        self.assertRaises(TypeError, transforma, 'not_valid')
        self.assertRaises(TypeError, transforma, 'auto', 1)

    def testSector(self):
        #sector [0-7]
        ss = self.mappercommands._sectorSelector
        self.mappercommands.sector()  # should print mapper state
        eq_(ss.sector, 0, "test assumes sector is 0 to start")
        self.mappercommands.sector(1)
        eq_(ss.sector, 1)
        self.assertRaises(TypeError, self.mappercommands.sector, 1, 2)
        self.assertRaises(TypeError, self.mappercommands.sector, 'a')

    def testAutosectors(self):
        #autosector [0-7]
        ss = self.sector_selector
        self.mappercommands.autosector()  # should print mapper state
        eq_(ss.autosectors, [], "test assumes no auto sectors to start")
        self.mappercommands.autosector(1)
        eq_(ss.autosectors, [1])
        self.mappercommands.autosector(1, 2)
        eq_(ss.autosectors, [1, 2])
        self.mappercommands.autosector(1)
        eq_(ss.autosectors, [1])
        self.mappercommands.autosector(3)
        eq_(ss.autosectors, [3])
        self.assertRaises(TypeError, self.mappercommands.autosector, 1, 'a')
        self.assertRaises(TypeError, self.mappercommands.autosector, 'a')

    def testSetcut(self):
        print "*******"
        self.mappercommands.setcut()
        print "*******"
        self.mappercommands.setcut('a')
        print "*******"
        self.mappercommands.setcut('a', -181)
        print "*******"
        eq_(self.mappercommands._hardware.getCuts()['a'], -181)
        self.assertRaises(
            ValueError, self.mappercommands.setcut, 'a', 'not a number')
        self.assertRaises(
            KeyError, self.mappercommands.setcut, 'not an axis', 1)
