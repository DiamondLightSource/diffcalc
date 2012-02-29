from diffcalc.hkl.vlieg.arm_to_base import gammaOnBaseToArm, gammaOnArmToBase
from diffcalc.hkl.vlieg.position import VliegPosition
from math import pi


TORAD = pi / 180
TODEG = 180 / pi


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


class SixCircleGammaOnArmGeometry(DiffractometerGeometryPlugin):
    """
    This six-circle diffractometer geometry simply passes through the
    angles from a six circle diffractometer with the same geometry and
    angle names as those defined in Vliegs's paper defined internally.
    """

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(
            self,
            name='sixc_gamma_on_arm',
            supportedModeGroupList=('fourc', 'fivecFixedGamma',
                                    'fivecFixedAlpha', 'zaxis'),
            fixedParameterDict={},
            gammaLocation='arm')

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 6), "Wrong length of input list"
        return VliegPosition(*physicalAngles)

    def internalPositionToPhysicalAngles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        return internalPosition.totuple()


class SixCircleGeometry(DiffractometerGeometryPlugin):
    """
    This six-circle diffractometer geometry simply passes through the
    angles from a six circle diffractometer with the same geometry and
    angle names as those defined in Vliegs's paper defined internally.
    """

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(
            self,
            name='sixc',
            supportedModeGroupList=('fourc', 'fivecFixedGamma',
                                    'fivecFixedAlpha', 'zaxis'),
            fixedParameterDict={},
            gammaLocation='base')
        self.hardwareMonitor = None
#(deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha) (all in radians)
#(deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha) (all in radians)

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 6), "Wrong length of input list"
        alpha, deltaB, gammaB, omega, chi, phi = physicalAngles
        (deltaA, gammaA) = gammaOnBaseToArm(
            deltaB * TORAD, gammaB * TORAD, alpha * TORAD)
        return VliegPosition(
            alpha, deltaA * TODEG, gammaA * TODEG, omega, chi, phi)

    def internalPositionToPhysicalAngles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        alpha, deltaA, gammaA, omega, chi, phi = internalPosition.totuple()
        deltaB, gammaB = gammaOnArmToBase(
            deltaA * TORAD, gammaA * TORAD, alpha * TORAD)
        deltaB, gammaB = deltaB * TODEG, gammaB * TODEG

        if self.hardwareMonitor is not None:
            gammaName = self.hardwareMonitor.getPhysicalAngleNames()[2]
            minGamma = self.hardwareMonitor.getLowerLimit(gammaName)
            maxGamma = self.hardwareMonitor.getUpperLimit(gammaName)

            if maxGamma is not None:
                if gammaB > maxGamma:
                    gammaB = gammaB - 180
                    deltaB = 180 - deltaB
            if minGamma is not None:
                if gammaB < minGamma:
                    gammaB = gammaB + 180
                    deltaB = 180 - deltaB

        return alpha, deltaB, gammaB, omega, chi, phi


class SixCircleYouGeometry(SixCircleGammaOnArmGeometry):
    def __init__(self):
        DiffractometerGeometryPlugin.__init__(
            self,
            name='sixc_you',
            supportedModeGroupList=('fourc', 'fivecFixedGamma',
                                    'fivecFixedAlpha', 'zaxis'),
            fixedParameterDict={},
            gammaLocation=None)


class FivecWithGammaOnBase(SixCircleGeometry):

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(
            self,
            name='fivec_with_gamma',
            supportedModeGroupList=('fourc', 'fivecFixedGamma'),
            fixedParameterDict={'alpha': 0.0},
            gammaLocation='base')
        self.hardwareMonitor = None

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(d,g,o,c,p)
        """
        assert (len(physicalAngles) == 5), "Wrong length of input list"
        return SixCircleGeometry.physicalAnglesToInternalPosition(
            self, (0,) + tuple(physicalAngles))

    def internalPositionToPhysicalAngles(self, internalPosition):
        """ (d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        return SixCircleGeometry.internalPositionToPhysicalAngles(
            self, internalPosition)[1:]


class fivec(DiffractometerGeometryPlugin):
    """
    This five-circle diffractometer geometry is for diffractometers with the
    same geometry and angle names as those defined in Vliegs's paper defined
    internally, but with no out plane detector arm  gamma."""

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(self,
                    name='fivec',
                    supportedModeGroupList=('fourc', 'fivecFixedGamma'),
                    fixedParameterDict={'gamma': 0.0},
                    gammaLocation='arm'
        )

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 5), "Wrong length of input list"
        physicalAngles = tuple(physicalAngles)
        angles = physicalAngles[0:2] + (0.0,) + physicalAngles[2:]
        return VliegPosition(*angles)

    def internalPositionToPhysicalAngles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        sixAngles = internalPosition.totuple()
        return sixAngles[0:2] + sixAngles[3:]


class fourc(DiffractometerGeometryPlugin):
    """
    This five-circle diffractometer geometry is for diffractometers with the
    same geometry and angle names as those defined in Vliegs's paper defined
    internally, but with no out plane detector arm  gamma."""

    def __init__(self):
        DiffractometerGeometryPlugin.__init__(self,
                    name='fourc',
                    supportedModeGroupList=('fourc'),
                    fixedParameterDict={'gamma': 0.0, 'alpha': 0.0},
                    gammaLocation='arm'
        )

    def physicalAnglesToInternalPosition(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 4), "Wrong length of input list"
        physicalAngles = tuple(physicalAngles)
        angles = (0.0, physicalAngles[0], 0.0) + physicalAngles[1:]
        return VliegPosition(*angles)

    def internalPositionToPhysicalAngles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        sixAngles = internalPosition.totuple()
        return sixAngles[1:2] + sixAngles[3:]
