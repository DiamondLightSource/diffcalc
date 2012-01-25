from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.mapper.commands import MapperCommands
from diffcalc.hkl.vlieg.position  import VliegPosition
import diffcalc.help #@UnusedImport
import unittest
from diffcalc.mapper.sector import SectorSelector
from diffcalc.mapper.mapper import PositionMapper

class TestAngleMapper(unittest.TestCase):

    def setUp(self):
        self.hardware = DummyHardwareMonitorPlugin(('a', 'd', 'g', 'o', 'c', 'phi'))
        self.geometry = SixCircleGammaOnArmGeometry()
        
        
        self.sector_selector = SectorSelector()
        self.position_mapper = PositionMapper(self.geometry, self.hardware, self.sector_selector)
        self.mappercommands = MapperCommands(self.geometry, self.hardware, self.sector_selector)

        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True

    def testMapDefaultSector(self):
        self.assertEquals(self.position_mapper.map(VliegPosition(1, 2, 3, 4, 5, 6)), (1, 2, 3, 4, 5, 6))
        self.assertEquals(self.position_mapper.map(VliegPosition(-180, -179, 0, 179, 180, 359)), (-180, -179, 0, 179, 180, 359))
        self.assertEquals(self.position_mapper.map(VliegPosition(0, 0, 0, 0, 0, 0)), (0, 0, 0, 0, 0, 0))
        self.assertEquals(self.position_mapper.map(VliegPosition(-270, 270, 0, 0, 0, -90)), (90, -90, 0, 0, 0, 270))

    def testMapSector1(self):
        self.mappercommands._sectorSelector.setSector(1)
        self.assertEquals(self.position_mapper.map(VliegPosition(1, 2, 3, 4, 5, 6)), (1, 2, 3, 4 - 180, -5, (6 - 180) + 360))
        self.assertEquals(self.position_mapper.map(VliegPosition(-180, -179, 0, 179, 180, 359)), (-180, -179, 0, 179 - 180, -180, 359 - 180))
        self.assertEquals(self.position_mapper.map(VliegPosition(0, 0, 0, 0, 0, 0)), (0, 0, 0, 0 - 180, 0, (0 - 180) + 360))
        self.assertEquals(self.position_mapper.map(VliegPosition(-270, 270, 0, 0, 0, -90)), (90, -90, 0, 0 - 180, 0, 270 - 180))
    
    def testMapAutoSector(self):
        self.mappercommands._sectorSelector.addAutoTransorm(1)
        self.hardware.setLowerLimit('c', 0)
        self.assertEquals(self.position_mapper.map(VliegPosition(1, 2, 3, 4, -5, 6)), (1, 2, 3, 4 - 180, 5, (6 - 180) + 360))
        self.assertEquals(self.position_mapper.map(VliegPosition(-180, -179, 0, 179, -180, 359)), (-180, -179, 0, 179 - 180, 180, 359 - 180))
        self.assertEquals(self.position_mapper.map(VliegPosition(0, 0, 0, 0, -5, 0)), (0, 0, 0, 0 - 180, 5, (0 - 180) + 360))
        self.assertEquals(self.position_mapper.map(VliegPosition(-270, 270, 0, 0, -5, -90)), (90, -90, 0, 0 - 180, 5, 270 - 180))

    def test_reprSectorLimits(self):
#        self.assertEqual(self.mappercommands._reprSectorLimits('alpha'), 'alpha')
#        self.mappercommands.setmin('alpha', -10)
#        self.assertEqual(self.mappercommands._reprSectorLimits('alpha'), '-10.000000 <= alpha')
#        self.mappercommands.setmin('alpha', None)
#        self.assertEqual(self.mappercommands._reprSectorLimits('alpha'), 'alpha')
#        self.mappercommands.setmax('alpha', 10)
#        self.assertEqual(self.mappercommands._reprSectorLimits('alpha'), 'alpha <= 10.000000')
#        self.mappercommands.setmin('alpha', -10)
#        self.assertEqual(self.mappercommands._reprSectorLimits('alpha'), '-10.000000 <= alpha <= 10.000000')
        
        self.mappercommands.setmin('phi', -1)
        print "*******"
        self.mappercommands.setmin()
        print "*******"
        self.mappercommands.setmax()
        print "*******"

    def testMapper(self):
        # mapper
        self.mappercommands.mapper() # should print its state
        self.assertRaises(TypeError, self.mappercommands.mapper, 1)
        self.assertRaises(TypeError, self.mappercommands.mapper, 'a', 1)

    def testTransformsOnOff(self):
        # transforma [on/off/auto/manual]
        ss = self.mappercommands._sectorSelector
        self.mappercommands.transforma() # should print mapper state
        self.assertEquals(ss.transforms, [], "test assumes transforms are off to start")
        self.mappercommands.transforma('on')
        self.assertEquals(ss.transforms, ['a'])
        self.mappercommands.transformb('on')
        self.assertEquals(ss.transforms, ['a', 'b'])
        self.mappercommands.transformc('off')
        self.assertEquals(ss.transforms, ['a', 'b'])
        self.mappercommands.transformb('off')
        self.assertEquals(ss.transforms, ['a'])

    def testTransformsAuto(self):
        ss = self.mappercommands._sectorSelector
        self.assertEquals(ss.autotransforms, [], "test assumes transforms are off to start")
        self.mappercommands.transforma('auto')
        self.assertEquals(ss.autotransforms, ['a'])
        self.mappercommands.transformb('auto')
        self.assertEquals(ss.autotransforms, ['a', 'b'])
        self.mappercommands.transformc('manual')
        self.assertEquals(ss.autotransforms, ['a', 'b'])
        self.mappercommands.transformb('manual')
        self.assertEquals(ss.autotransforms, ['a'])
    
    def testTransformsBadInput(self):
        self.assertRaises(TypeError, self.mappercommands.transforma, 1)
        self.assertRaises(TypeError, self.mappercommands.transforma, 'not_valid')
        self.assertRaises(TypeError, self.mappercommands.transforma, 'auto', 1)

    def testSector(self):
        #sector [0-7]
        ss = self.mappercommands._sectorSelector
        self.mappercommands.sector() # should print mapper state
        self.assertEquals(ss.sector, 0, "test assumes sector is 0 to start")
        self.mappercommands.sector(1)
        self.assertEquals(ss.sector, 1)
        self.assertRaises(TypeError, self.mappercommands.sector, 1, 2)
        self.assertRaises(TypeError, self.mappercommands.sector, 'a')

    def testAutosectors(self):
        #autosector [0-7]
        ss = self.sector_selector
        self.mappercommands.autosector() # should print mapper state
        self.assertEquals(ss.autosectors, [], "test assumes no auto sectors to start")
        self.mappercommands.autosector(1)
        self.assertEquals(ss.autosectors, [1])
        self.mappercommands.autosector(1, 2)
        self.assertEquals(ss.autosectors, [1, 2])
        self.mappercommands.autosector(1)
        self.assertEquals(ss.autosectors, [1])
        self.mappercommands.autosector(3)
        self.assertEquals(ss.autosectors, [3])
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
        self.assertEquals(self.mappercommands._hardware.getCuts()['a'], -181)
        self.assertRaises(ValueError, self.mappercommands.setcut, 'a', 'not a number')
        self.assertRaises(KeyError, self.mappercommands.setcut, 'not an axis', 1)
