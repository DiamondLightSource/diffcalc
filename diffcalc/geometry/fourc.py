from plugin import DiffractometerGeometryPlugin
from diffcalc.utils import Position

class fourc(DiffractometerGeometryPlugin):
    """This five-circle diffractometer geometry is for diffractometers with the same
    geometry and angle names as those defined in Vliegs's paper defined internally, but
    with no out plane detector arm  gamma."""

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(self, 
                    name = 'fourc', 
                    supportedModeGroupList = ('fourc'), 
                    fixedParameterDict = {'gamma':0.0, 'alpha':0.0}, 
                    gammaLocation = 'arm'
                    )

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles)==4), "Wrong length of input list"
        # 
        physicalAngles = tuple(physicalAngles)
        angles = (0.0, physicalAngles[0], 0.0) + physicalAngles[1:]
        return Position(*angles)
    
    def internalPositionToPhysicalAngles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        sixAngles = internalPosition.totuple()
        return sixAngles[1:2] + sixAngles[3:]
