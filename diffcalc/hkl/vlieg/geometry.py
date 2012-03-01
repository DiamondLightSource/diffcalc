from diffcalc.hkl.vlieg.arm_to_base import gammaOnBaseToArm, gammaOnArmToBase
from diffcalc.hkl.vlieg.position import VliegPosition
from math import pi


TORAD = pi / 180
TODEG = 180 / pi


class VliegGeometry(object):

# Required methods

    def __init__(self, name, supported_mode_groups, fixed_parameters,
                 gamma_location):
        """
        Set geometry name (String), list of supported mode groups (list of
        strings), list of axis names (list of strings). Define the parameters
        e.g. alpha and gamma for a four circle (dictionary). Define wether the
        gamma angle is on the 'arm' or the 'base'; used only by AngleCalculator
        to interpret the gamma parameter in fixed gamma mode: for instruments
        with gamma on the base, rather than on the arm as the code assume
        internally, the two methods physical_angles_to_internal_position and
        internal_position_to_physical_angles must still be used.
        """
        if gamma_location not in ('arm', 'base', None):
            raise RuntimeError(
                "Gamma must be on either 'arm' or 'base' or None")

        self.name = name
        self.supported_mode_groups = supported_mode_groups
        self.fixed_parameters = fixed_parameters
        self.gamma_location = gamma_location

    def physical_angles_to_internal_position(self, physicalAngles):
        raise NotImplementedError()

    def internal_position_to_physical_angles(self, physicalAngles):
        raise NotImplementedError()

### Do not overide these these ###

    def supports_mode_group(self, name):
        return name in self.supported_mode_groups

    def parameter_fixed(self, name):  # parameter_fixed
        return name in self.fixed_parameters.keys()


class SixCircleGammaOnArmGeometry(VliegGeometry):
    """
    This six-circle diffractometer geometry simply passes through the
    angles from a six circle diffractometer with the same geometry and
    angle names as those defined in Vliegs's paper defined internally.
    """

    def __init__(self):
        VliegGeometry.__init__(
            self,
            name='sixc_gamma_on_arm',
            supported_mode_groups=('fourc', 'fivecFixedGamma',
                                    'fivecFixedAlpha', 'zaxis'),
            fixed_parameters={},
            gamma_location='arm')

    def physical_angles_to_internal_position(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 6), "Wrong length of input list"
        return VliegPosition(*physicalAngles)

    def internal_position_to_physical_angles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        return internalPosition.totuple()


class SixCircleGeometry(VliegGeometry):
    """
    This six-circle diffractometer geometry simply passes through the
    angles from a six circle diffractometer with the same geometry and
    angle names as those defined in Vliegs's paper defined internally.
    """

    def __init__(self):
        VliegGeometry.__init__(
            self,
            name='sixc',
            supported_mode_groups=('fourc', 'fivecFixedGamma',
                                    'fivecFixedAlpha', 'zaxis'),
            fixed_parameters={},
            gamma_location='base')
        self.hardwareMonitor = None
#(deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha) (all in radians)
#(deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha) (all in radians)

    def physical_angles_to_internal_position(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 6), "Wrong length of input list"
        alpha, deltaB, gammaB, omega, chi, phi = physicalAngles
        (deltaA, gammaA) = gammaOnBaseToArm(
            deltaB * TORAD, gammaB * TORAD, alpha * TORAD)
        return VliegPosition(
            alpha, deltaA * TODEG, gammaA * TODEG, omega, chi, phi)

    def internal_position_to_physical_angles(self, internalPosition):
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
        VliegGeometry.__init__(
            self,
            name='fivec_with_gamma',
            supported_mode_groups=('fourc', 'fivecFixedGamma'),
            fixed_parameters={'alpha': 0.0},
            gamma_location='base')
        self.hardwareMonitor = None

    def physical_angles_to_internal_position(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(d,g,o,c,p)
        """
        assert (len(physicalAngles) == 5), "Wrong length of input list"
        return SixCircleGeometry.physical_angles_to_internal_position(
            self, (0,) + tuple(physicalAngles))

    def internal_position_to_physical_angles(self, internalPosition):
        """ (d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        return SixCircleGeometry.internal_position_to_physical_angles(
            self, internalPosition)[1:]


class Fivec(VliegGeometry):
    """
    This five-circle diffractometer geometry is for diffractometers with the
    same geometry and angle names as those defined in Vliegs's paper defined
    internally, but with no out plane detector arm  gamma."""

    def __init__(self):
        VliegGeometry.__init__(self,
                    name='fivec',
                    supported_mode_groups=('fourc', 'fivecFixedGamma'),
                    fixed_parameters={'gamma': 0.0},
                    gamma_location='arm'
        )

    def physical_angles_to_internal_position(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 5), "Wrong length of input list"
        physicalAngles = tuple(physicalAngles)
        angles = physicalAngles[0:2] + (0.0,) + physicalAngles[2:]
        return VliegPosition(*angles)

    def internal_position_to_physical_angles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        sixAngles = internalPosition.totuple()
        return sixAngles[0:2] + sixAngles[3:]


class Fourc(VliegGeometry):
    """
    This five-circle diffractometer geometry is for diffractometers with the
    same geometry and angle names as those defined in Vliegs's paper defined
    internally, but with no out plane detector arm  gamma."""

    def __init__(self):
        VliegGeometry.__init__(self,
                    name='fourc',
                    supported_mode_groups=('fourc'),
                    fixed_parameters={'gamma': 0.0, 'alpha': 0.0},
                    gamma_location='arm'
        )

    def physical_angles_to_internal_position(self, physicalAngles):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        assert (len(physicalAngles) == 4), "Wrong length of input list"
        physicalAngles = tuple(physicalAngles)
        angles = (0.0, physicalAngles[0], 0.0) + physicalAngles[1:]
        return VliegPosition(*angles)

    def internal_position_to_physical_angles(self, internalPosition):
        """ (a,d,g,o,c,p) = physicalAnglesToInternal(a,d,g,o,c,p)
        """
        sixAngles = internalPosition.totuple()
        return sixAngles[1:2] + sixAngles[3:]
