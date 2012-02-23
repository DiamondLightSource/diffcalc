class DiffractometerGeometryPlugin(object):

# Required methods

    def __init__(self, name, supportedModeGroupList, fixedParameterDict,
                 gammaLocation, mirrorInXzPlane=False):
        """
        Set geometry name (String), list of supported mode groups (list of
        strings), list of axis names (list of strings). Define the parameters
        e.g. alpha and gamma for a four circle (dictionary). Define wether the
        gamma angle is on the 'arm' or the 'base'; used only by AngleCalculator
        to interpret the gamma parameter in fixed gamma mode: for instruments
        with gamma on the base, rather than on the arm as the code assume
        internally, the two methods physicalAnglesToInternalPosition and
        internalPositionToPhysicalAngles must still be used.
        """
        if gammaLocation not in ('arm', 'base', None):
            raise RuntimeError(
                "Gamma must be on either 'arm' or 'base' or None")

        self._name = name
        self._supportedModeGroupList = supportedModeGroupList
        self._fixedParameterDict = fixedParameterDict
        self._gammaLocation = gammaLocation
        self.mirrorInXzPlane = mirrorInXzPlane

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """internalAngles = physicalToInternal(physical)"""
        raise RuntimeError("Calling base class")

    def internalPositionToPhysicalAngles(self, physicalAngles):
        """internalAngles = physicalToInternal(physical)"""
        raise RuntimeError("Calling base class")

### Do not overide these these ###

    def getName(self):
        return self._name

    def supportsModeGroup(self, name):
        return name in self._supportedModeGroupList

    def getSupportedModeGroups(self):
        return self._supportedModeGroupList

    def isParameterFixed(self, name):  # isParameterFixed
        return name in self._fixedParameterDict.keys()

    def getFixedParameters(self):
        return self._fixedParameterDict

    def gammaLocation(self):
        """AngleCalculator will use this flag to determine how
        """
        return self._gammaLocation
