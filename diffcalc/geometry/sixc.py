from diffcalc.geometry.plugin import DiffractometerGeometryPlugin
from diffcalc.hkl.vlieg.position  import VliegPosition
from diffcalc.utils import nearlyEqual, bound
from math import tan, cos, sin, asin, atan, pi, fabs

TORAD = pi / 180
TODEG = 180 / pi


def sign(x):
    if x < 0:
        return -1
    else:
        return 1


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


class SixCircleYouGeometry(SixCircleGammaOnArmGeometry):
    def __init__(self):
        DiffractometerGeometryPlugin.__init__(
            self,
            name='sixc_you',
            supportedModeGroupList=('fourc', 'fivecFixedGamma',
                                    'fivecFixedAlpha', 'zaxis'),
            fixedParameterDict={},
            gammaLocation=None)


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


"""
Based on: Elias Vlieg, "A (2+3)-Type Surface Diffractometer: Mergence of
the z-axis and (2+2)-Type Geometries", J. Appl. Cryst. (1998). 31.
198-203
"""

max_gamma = pi
min_gamma = 0


def solvesEq8(alpha, deltaA, gammaA, deltaB, gammaB):
    tol = 1e-6
    return (nearlyEqual(sin(deltaA) * cos(gammaA), sin(deltaB), tol) and
        nearlyEqual(cos(deltaA) * cos(gammaA),
                    cos(gammaB - alpha) * cos(deltaB), tol) and
        nearlyEqual(sin(gammaA), sin(gammaB - alpha) * cos(deltaB), tol))


GAMMAONBASETOARM_WARNING = '''
WARNING: This diffractometer has the gamma circle attached to the
         base rather than the end of
         the delta arm as Vlieg's paper defines. A conversion has
         been made from the physical angles to their internal
         representation (gamma-on-base-to-arm). This conversion has
         forced gamma to be positive by applying the mapping:

         delta --> 180+delta
         gamma --> 180+gamma.

         This should have no adverse effect.
'''


def gammaOnBaseToArm(deltaB, gammaB, alpha):
    """
    (deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha) (all in
    radians)

    Maps delta and gamma for an instrument where the gamma circle rests on
    the base to the case where it is on the delta arm.

    There are always two possible solutions. To get the second apply the
    transform:

        delta --> 180+delta (flip to opposite side of circle)
        gamma --> 180+gamma (flip to opposite side of circle)

    This code will return the solution where gamma is between 0 and 180.
    """

    ### Equation11 ###
    if fabs(cos(gammaB - alpha)) < 1e-20:
        deltaA1 = sign(tan(deltaB)) * sign(cos(gammaB - alpha)) * pi / 2
    else:
        deltaA1 = atan(tan(deltaB) / cos(gammaB - alpha))
    # ...second root
    if deltaA1 <= 0:
        deltaA2 = deltaA1 + pi
    else:
        deltaA2 = deltaA1 - pi

    ### Equation 12 ###
    gammaA1 = asin(bound(cos(deltaB) * sin(gammaB - alpha)))
    # ...second root
    if gammaA1 >= 0:
        gammaA2 = pi - gammaA1
    else:
        gammaA2 = -pi - gammaA1

    # Choose the delta solution that fits equations 8
    if solvesEq8(alpha, deltaA1, gammaA1, deltaB, gammaB):
        deltaA, gammaA = deltaA1, gammaA1
    elif solvesEq8(alpha, deltaA2, gammaA1, deltaB, gammaB):
        deltaA, gammaA = deltaA2, gammaA1
        print "gammaOnBaseToArm choosing 2nd delta root (to internal)"
    elif solvesEq8(alpha, deltaA1, gammaA2, deltaB, gammaB):
        print "gammaOnBaseToArm choosing 2nd gamma root (to internal)"
        deltaA, gammaA = deltaA1, gammaA2
    elif solvesEq8(alpha, deltaA2, gammaA2, deltaB, gammaB):
        print "gammaOnBaseToArm choosing 2nd delta root and 2nd gamma root"
        deltaA, gammaA = deltaA2, gammaA2
    else:
        raise RuntimeError(
         "No valid solutions found mapping from gamma-on-base to gamma-on-arm")

    return deltaA, gammaA

GAMMAONARMTOBASE_WARNING = '''
        WARNING: This diffractometer has the gamma circle attached to the base
                 rather than the end of the delta arm as Vlieg's paper defines.
                 A conversion has been made from the internal representation of
                 angles to physical angles (gamma-on-arm-to-base). This
                 conversion has forced gamma to be positive by applying the
                 mapping:

                    delta --> 180-delta
                    gamma --> 180+gamma.

                 This should have no adverse effect.
'''


def gammaOnArmToBase(deltaA, gammaA, alpha):
    """
    (deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha) (all in
    radians)

    Maps delta and gamma for an instrument where the gamma circle is on
    the delta arm to the case where it rests on the base.

    There are always two possible solutions. To get the second apply the
    transform:

        delta --> 180-delta (reflect and flip to opposite side)
        gamma --> 180+gamma (flip to opposite side)

    This code will return the solution where gamma is positive, but will
    warn if a sign change was made.
    """

    ### Equation 9 ###
    deltaB1 = asin(bound(sin(deltaA) * cos(gammaA)))
    # ...second root:
    if deltaB1 >= 0:
        deltaB2 = pi - deltaB1
    else:
        deltaB2 = -pi - deltaB1

    ### Equation 10 ###:
    if fabs(cos(deltaA)) < 1e-20:
        gammaB1 = sign(tan(gammaA)) * sign(cos(deltaA)) * pi / 2 + alpha
    else:
        gammaB1 = atan(tan(gammaA) / cos(deltaA)) + alpha
    #... second root:
    if gammaB1 <= 0:
        gammaB2 = gammaB1 + pi
    else:
        gammaB2 = gammaB1 - pi

    ### Choose the solution that fits equation 8 ###
    if (solvesEq8(alpha, deltaA, gammaA, deltaB1, gammaB1) and
        0 <= gammaB1 <= pi):
        deltaB, gammaB = deltaB1, gammaB1
    elif (solvesEq8(alpha, deltaA, gammaA, deltaB2, gammaB1) and
          0 <= gammaB1 <= pi):
        deltaB, gammaB = deltaB2, gammaB1
        print "gammaOnArmToBase choosing 2nd delta root (to physical)"
    elif (solvesEq8(alpha, deltaA, gammaA, deltaB1, gammaB2) and
          0 <= gammaB2 <= pi):
        print "gammaOnArmToBase choosing 2nd gamma root (to physical)"
        deltaB, gammaB = deltaB1, gammaB2
    elif (solvesEq8(alpha, deltaA, gammaA, deltaB2, gammaB2)
          and 0 <= gammaB2 <= pi):
        print "gammaOnArmToBase choosing 2nd delta root and 2nd gamma root"
        deltaB, gammaB = deltaB2, gammaB2
    else:
        raise RuntimeError(
            "No valid solutions found mapping gamma-on-arm to gamma-on-base")

    return deltaB, gammaB
