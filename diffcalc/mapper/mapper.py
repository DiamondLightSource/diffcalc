class PositionMapper(object):

    def __init__(self, geometry, hardware, sector_selector):
        self._geometry = geometry
        self._hardware = hardware
        self._sector_selector = sector_selector
        sector_selector.limitCheckerFunction = self.isPositionWithinLimits

    def map(self, pos):  # @ReservedAssignment
        '''
        Maps a Position object (in degrees) into a physical diffractometer
        setting'''
        # 1. Choose the correct sector/transforms
        pos = self._sector_selector.transformPosition(pos)
        angleTuple = self._geometry.internalPositionToPhysicalAngles(pos)
        angleTuple = self._hardware.cutAngles(angleTuple)
        return angleTuple

    def isPositionWithinLimits(self, position):
        '''where position is Position object in degrees'''
        angleTuple = self._geometry.internalPositionToPhysicalAngles(position)
        angleTuple = self._hardware.cutAngles(angleTuple)
        return self._hardware.isPositionWithinLimits(angleTuple)
