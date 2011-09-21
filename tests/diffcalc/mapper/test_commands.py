from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.mapper.commands import MapperCommands
from diffcalc.utils import Position
import diffcalc.help #@UnusedImport
import unittest

class TestAngleMapper(unittest.TestCase):

    def setUp(self):
        self.hardware = DummyHardwareMonitorPlugin(('a', 'd', 'g', 'o', 'c', 'phi'))
        self.geometry = SixCircleGammaOnArmGeometry()
        self.mapper_commands = MapperCommands(self.geometry, self.hardware)
        diffcalc.help.RAISE_EXCEPTIONS_FOR_ALL_ERRORS = True

    def testMapDefaultSector(self):
        self.assertEquals(self.mapper_commands.map(Position(1, 2, 3, 4, 5, 6)), (1, 2, 3, 4, 5, 6))
        self.assertEquals(self.mapper_commands.map(Position(-180, -179, 0, 179, 180, 359)), (-180, -179, 0, 179, 180, 359))
        self.assertEquals(self.mapper_commands.map(Position(0, 0, 0, 0, 0, 0)), (0, 0, 0, 0, 0, 0))
        self.assertEquals(self.mapper_commands.map(Position(-270, 270, 0, 0, 0, -90)), (90, -90, 0, 0, 0, 270))

    def testMapSector1(self):
        self.mapper_commands._sectorSelector.setSector(1)
        self.assertEquals(self.mapper_commands.map(Position(1, 2, 3, 4, 5, 6)), (1, 2, 3, 4 - 180, -5, (6 - 180) + 360))
        self.assertEquals(self.mapper_commands.map(Position(-180, -179, 0, 179, 180, 359)), (-180, -179, 0, 179 - 180, -180, 359 - 180))
        self.assertEquals(self.mapper_commands.map(Position(0, 0, 0, 0, 0, 0)), (0, 0, 0, 0 - 180, 0, (0 - 180) + 360))
        self.assertEquals(self.mapper_commands.map(Position(-270, 270, 0, 0, 0, -90)), (90, -90, 0, 0 - 180, 0, 270 - 180))
    
    def testMapAutoSector(self):
        self.mapper_commands._sectorSelector.addAutoTransorm(1)
        self.hardware.setLowerLimit('c', 0)
        self.assertEquals(self.mapper_commands.map(Position(1, 2, 3, 4, -5, 6)), (1, 2, 3, 4 - 180, 5, (6 - 180) + 360))
        self.assertEquals(self.mapper_commands.map(Position(-180, -179, 0, 179, -180, 359)), (-180, -179, 0, 179 - 180, 180, 359 - 180))
        self.assertEquals(self.mapper_commands.map(Position(0, 0, 0, 0, -5, 0)), (0, 0, 0, 0 - 180, 5, (0 - 180) + 360))
        self.assertEquals(self.mapper_commands.map(Position(-270, 270, 0, 0, -5, -90)), (90, -90, 0, 0 - 180, 5, 270 - 180))

    def test_reprSectorLimits(self):
#        self.assertEqual(self.mapper_commands._reprSectorLimits('alpha'), 'alpha')
#        self.mapper_commands.setmin('alpha', -10)
#        self.assertEqual(self.mapper_commands._reprSectorLimits('alpha'), '-10.000000 <= alpha')
#        self.mapper_commands.setmin('alpha', None)
#        self.assertEqual(self.mapper_commands._reprSectorLimits('alpha'), 'alpha')
#        self.mapper_commands.setmax('alpha', 10)
#        self.assertEqual(self.mapper_commands._reprSectorLimits('alpha'), 'alpha <= 10.000000')
#        self.mapper_commands.setmin('alpha', -10)
#        self.assertEqual(self.mapper_commands._reprSectorLimits('alpha'), '-10.000000 <= alpha <= 10.000000')
        
        self.mapper_commands.setmin('phi', -1)
        print "*******"
        self.mapper_commands.setmin()
        print "*******"
        self.mapper_commands.setmax()
        print "*******"

    def testMapper(self):
        # mapper
        self.mapper_commands.mapper() # should print its state
        self.assertRaises(TypeError, self.mapper_commands.mapper, 1)
        self.assertRaises(TypeError, self.mapper_commands.mapper, 'a', 1)

    def testTransformsOnOff(self):
        # transforma [on/off/auto/manual]
        ss = self.mapper_commands._sectorSelector
        self.mapper_commands.transforma() # should print mapper state
        self.assertEquals(ss.transforms, [], "test assumes transforms are off to start")
        self.mapper_commands.transforma('on')
        self.assertEquals(ss.transforms, ['a'])
        self.mapper_commands.transformb('on')
        self.assertEquals(ss.transforms, ['a', 'b'])
        self.mapper_commands.transformc('off')
        self.assertEquals(ss.transforms, ['a', 'b'])
        self.mapper_commands.transformb('off')
        self.assertEquals(ss.transforms, ['a'])

    def testTransformsAuto(self):
        ss = self.mapper_commands._sectorSelector
        self.assertEquals(ss.autotransforms, [], "test assumes transforms are off to start")
        self.mapper_commands.transforma('auto')
        self.assertEquals(ss.autotransforms, ['a'])
        self.mapper_commands.transformb('auto')
        self.assertEquals(ss.autotransforms, ['a', 'b'])
        self.mapper_commands.transformc('manual')
        self.assertEquals(ss.autotransforms, ['a', 'b'])
        self.mapper_commands.transformb('manual')
        self.assertEquals(ss.autotransforms, ['a'])
    
    def testTransformsBadInput(self):
        self.assertRaises(TypeError, self.mapper_commands.transforma, 1)
        self.assertRaises(TypeError, self.mapper_commands.transforma, 'not_valid')
        self.assertRaises(TypeError, self.mapper_commands.transforma, 'auto', 1)

    def testSector(self):
        #sector [0-7]
        ss = self.mapper_commands._sectorSelector
        self.mapper_commands.sector() # should print mapper state
        self.assertEquals(ss.sector, 0, "test assumes sector is 0 to start")
        self.mapper_commands.sector(1)
        self.assertEquals(ss.sector, 1)
        self.assertRaises(TypeError, self.mapper_commands.sector, 1, 2)
        self.assertRaises(TypeError, self.mapper_commands.sector, 'a')

    def testAutosectors(self):
        #autosector [0-7]
        ss = self.mapper_commands._sectorSelector
        self.mapper_commands.autosector() # should print mapper state
        self.assertEquals(ss.autosectors, [], "test assumes no auto sectors to start")
        self.mapper_commands.autosector(1)
        self.assertEquals(ss.autosectors, [1])
        self.mapper_commands.autosector(1, 2)
        self.assertEquals(ss.autosectors, [1, 2])
        self.mapper_commands.autosector(1)
        self.assertEquals(ss.autosectors, [1])
        self.mapper_commands.autosector(3)
        self.assertEquals(ss.autosectors, [3])
        self.assertRaises(TypeError, self.mapper_commands.autosector, 1, 'a')
        self.assertRaises(TypeError, self.mapper_commands.autosector, 'a')

    def testSetcut(self):
        print "*******"
        self.mapper_commands.setcut()
        print "*******"
        self.mapper_commands.setcut('a')
        print "*******"
        self.mapper_commands.setcut('a', -181)
        print "*******"
        self.assertEquals(self.mapper_commands._hardware.getCuts()['a'], -181)
        self.assertRaises(ValueError, self.mapper_commands.setcut, 'a', 'not a number')
        self.assertRaises(KeyError, self.mapper_commands.setcut, 'not an axis', 1)
