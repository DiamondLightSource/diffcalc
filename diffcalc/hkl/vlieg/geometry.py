###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from math import tan, cos, sin, asin, atan, pi, fabs

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.util import x_rotation, z_rotation, y_rotation
from diffcalc.util import AbstractPosition
from diffcalc.util import bound, nearlyEqual


TORAD = pi / 180
TODEG = 180 / pi


def calcALPHA(alpha):
    return x_rotation(alpha)


def calcDELTA(delta):
    return z_rotation(-delta)


def calcGAMMA(gamma):
    return x_rotation(gamma)


def calcOMEGA(omega):
    return z_rotation(-omega)


def calcCHI(chi):
    return y_rotation(chi)


def calcPHI(phi):
    return z_rotation(-phi)


def createVliegMatrices(alpha=None, delta=None, gamma=None, omega=None,
                        chi=None, phi=None):

    ALPHA = None if alpha is None else calcALPHA(alpha)
    DELTA = None if delta is None else calcDELTA(delta)
    GAMMA = None if gamma is None else calcGAMMA(gamma)
    OMEGA = None if omega is None else calcOMEGA(omega)
    CHI = None if chi is None else calcCHI(chi)
    PHI = None if phi is None else calcPHI(phi)
    return ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI


def createVliegsSurfaceTransformationMatrices(sigma, tau):
    """[SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(sigma, tau)
    angles in radians
    """
    SIGMA = matrix([[cos(sigma), 0, sin(sigma)],
                    [0, 1, 0], \
                    [-sin(sigma), 0, cos(sigma)]])

    TAU = matrix([[cos(tau), sin(tau), 0],
                  [-sin(tau), cos(tau), 0],
                  [0, 0, 1]])
    return(SIGMA, TAU)


def createVliegsPsiTransformationMatrix(psi):
    """PSI = createPsiTransformationMatrices(psi)
    angles in radians
    """
    return matrix([[1, 0, 0],
                   [0, cos(psi), sin(psi)],
                   [0, -sin(psi), cos(psi)]])


class VliegPosition(AbstractPosition):
    """The position of all six diffractometer axis"""
    def __init__(self, alpha=None, delta=None, gamma=None, omega=None,
                 chi=None, phi=None):
        self.alpha = alpha
        self.delta = delta
        self.gamma = gamma
        self.omega = omega
        self.chi = chi
        self.phi = phi

    def clone(self):
        return VliegPosition(self.alpha, self.delta, self.gamma, self.omega,
                             self.chi, self.phi)

    def changeToRadians(self):
        self.alpha *= TORAD
        self.delta *= TORAD
        self.gamma *= TORAD
        self.omega *= TORAD
        self.chi *= TORAD
        self.phi *= TORAD

    def changeToDegrees(self):
        self.alpha *= TODEG
        self.delta *= TODEG
        self.gamma *= TODEG
        self.omega *= TODEG
        self.chi *= TODEG
        self.phi *= TODEG

    def inRadians(self):
        pos = self.clone()
        pos.changeToRadians()
        return pos

    def inDegrees(self):
        pos = self.clone()
        pos.changeToDegrees()
        return pos

    def nearlyEquals(self, pos2, maxnorm):
        for a, b in zip(self.totuple(), pos2.totuple()):
            if abs(a - b) > maxnorm:
                return False
        return True

    def totuple(self):
        return (self.alpha, self.delta, self.gamma, self.omega,
                self.chi, self.phi)

    def __str__(self):
        return ("VliegPosition(alpha %r delta: %r gamma: %r omega: %r chi: %r"
                "  phi: %r)" % self.totuple())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, b):
        return self.nearlyEquals(b, .001)


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
            gammaName = self.hardwareMonitor.get_axes_names()[2]
            minGamma = self.hardwareMonitor.get_lower_limit(gammaName)
            maxGamma = self.hardwareMonitor.get_upper_limit(gammaName)

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


def sign(x):
    if x < 0:
        return -1
    else:
        return 1

"""
Based on: Elias Vlieg, "A (2+3)-Type Surface Diffractometer: Mergence of
the z-axis and (2+2)-Type Geometries", J. Appl. Cryst. (1998). 31.
198-203
"""


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
