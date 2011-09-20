import unittest
from diffcalc.mapper.commands import MapperCommands
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry
from diffcalc.hardware.dummy import DummyHardwareMonitorPlugin
from diffcalc.utils import Position

class TestAngleMapper(unittest.TestCase):

    def setUp(self):
        self.hardware = DummyHardwareMonitorPlugin(('a','d','g','o','c','phi'))
        self.geometry = SixCircleGammaOnArmGeometry()
        self.mapper = MapperCommands(self.geometry, self.hardware)

    def testMapDefaultSector(self):
        self.assertEquals(self.mapper.map(Position(1,2,3,4,5,6)), (1,2,3,4,5,6) )
        self.assertEquals(self.mapper.map(Position(-180, -179, 0, 179, 180, 359)), (-180, -179, 0, 179, 180, 359) )
        self.assertEquals(self.mapper.map(Position(0, 0, 0, 0, 0, 0)), (0, 0, 0, 0, 0, 0) )
        self.assertEquals(self.mapper.map(Position(-270, 270, 0, 0, 0, -90)), (90, -90, 0, 0, 0, 270) )

    def testMapSector1(self):
        self.mapper._sectorSelector.setSector(1)
        self.assertEquals(self.mapper.map(Position(1,2,3,4,5,6)), (1,2,3,4-180,-5,(6-180)+360) )
        self.assertEquals(self.mapper.map(Position(-180, -179, 0, 179, 180, 359)), (-180, -179, 0, 179-180, -180, 359-180) )
        self.assertEquals(self.mapper.map(Position(0, 0, 0, 0, 0, 0)), (0, 0, 0, 0-180, 0, (0-180)+360) )
        self.assertEquals(self.mapper.map(Position(-270, 270, 0, 0, 0, -90)), (90, -90, 0, 0-180, 0, 270-180) )
    
    def testMapAutoSector(self):
        self.mapper._sectorSelector.addAutoTransorm(1)
        self.hardware.setLowerLimit('c', 0)
        self.assertEquals(self.mapper.map(Position(1,2,3,4,-5,6)), (1,2,3,4-180,5,(6-180)+360) )
        self.assertEquals(self.mapper.map(Position(-180, -179, 0, 179, -180, 359)), (-180, -179, 0, 179-180, 180, 359-180) )
        self.assertEquals(self.mapper.map(Position(0, 0, 0, 0, -5, 0)), (0, 0, 0, 0-180, 5, (0-180)+360) )
        self.assertEquals(self.mapper.map(Position(-270, 270, 0, 0, -5, -90)), (90, -90, 0, 0-180, 5, 270-180) )
