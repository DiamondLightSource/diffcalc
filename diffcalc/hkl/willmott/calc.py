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

from math import pi, asin, acos, atan2, sin, cos, sqrt

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.log import logging
from diffcalc.util import bound, AbstractPosition, DiffcalcException,\
    x_rotation, z_rotation
from diffcalc.hkl.vlieg.geometry import VliegGeometry
from diffcalc.ub.calc import PaperSpecificUbCalcStrategy
from diffcalc.hkl.calcbase import HklCalculatorBase
from diffcalc.hkl.common import DummyParameterManager

logger = logging.getLogger("diffcalc.hkl.willmot.calcwill")

CHOOSE_POSITIVE_GAMMA = True

TORAD = pi / 180
TODEG = 180 / pi
I = matrix('1 0 0; 0 1 0; 0 0 1')
SMALL = 1e-10

TEMPORARY_CONSTRAINTS_DICT_RAD = {'betain': 2 * TORAD}


def create_matrices(delta, gamma, omegah, phi):
    return (calc_DELTA(delta), calc_GAMMA(gamma), calc_OMEGAH(omegah),
            calc_PHI(phi))


def calc_DELTA(delta):
    return x_rotation(delta)                                             # (39)


def calc_GAMMA(gamma):
    return z_rotation(gamma)                                             # (40)


def calc_OMEGAH(omegah):
    return x_rotation(omegah)                                            # (41)


def calc_PHI(phi):
    return z_rotation(phi)                                               # (42)


def angles_to_hkl_phi(delta, gamma, omegah, phi):
    """Calculate hkl matrix in phi frame in units of 2*pi/lambda
    """
    DELTA, GAMMA, OMEGAH, PHI = create_matrices(delta, gamma, omegah, phi)
    H_lab = (GAMMA * DELTA - I) * matrix([[0], [1], [0]])                # (43)
    H_phi = PHI.I * OMEGAH.I * H_lab                                     # (44)
    return H_phi


def angles_to_hkl(delta, gamma, omegah, phi, wavelength, UB):
    """Calculate hkl matrix in reprical lattice space in units of 1/Angstrom
    """
    H_phi = angles_to_hkl_phi(delta, gamma, omegah, phi) * 2 * pi / wavelength
    hkl = UB.I * H_phi                                                    # (5)
    return hkl


class WillmottHorizontalPosition(AbstractPosition):

    def __init__(self, delta=None, gamma=None, omegah=None, phi=None):
        self.delta = delta
        self.gamma = gamma
        self.omegah = omegah
        self.phi = phi

    def clone(self):
        return WillmottHorizontalPosition(self.delta, self.gamma, self.omegah,
                                          self.phi)

    def changeToRadians(self):
        self.delta *= TORAD
        self.gamma *= TORAD
        self.omegah *= TORAD
        self.phi *= TORAD

    def changeToDegrees(self):
        self.delta *= TODEG
        self.gamma *= TODEG
        self.omegah *= TODEG
        self.phi *= TODEG

    def totuple(self):
        return (self.delta, self.gamma, self.omegah, self.phi)

    def __str__(self):
        return ('WillmottHorizontalPosition('
                'delta: %.4f gamma: %.4f omegah: %.4f phi: %.4f)' %
                (self.delta, self.gamma, self.omegah, self.phi))


class WillmottHorizontalGeometry(object):

    def __init__(self):
        self.name = 'willmott_horizontal'

    def physical_angles_to_internal_position(self, physicalAngles):
        return WillmottHorizontalPosition(*physicalAngles)

    def internal_position_to_physical_angles(self, internalPosition):
        return internalPosition.totuple()

    def create_position(self, delta, gamma, omegah, phi):
        return WillmottHorizontalPosition(delta, gamma, omegah, phi)


class WillmottHorizontalUbCalcStrategy(PaperSpecificUbCalcStrategy):

    def calculate_q_phi(self, pos):
        H_phi = angles_to_hkl_phi(*pos.totuple())
        return matrix(H_phi.tolist())


class DummyConstraints(object):

    @property
    def reference(self):
        """dictionary of constrained reference circles"""
        return TEMPORARY_CONSTRAINTS_DICT_RAD


class ConstraintAdapter(object):

    def __init__(self, constraints):
        self._constraints = constraints

    def getParameterDict(self):
        names = self._constraints.available
        return dict(zip(names, [None] * len(names)))

    def setParameter(self, name, value):
        self._constraints.set_constraint(name, value)

    def get(self, name):
        if name in self._constraints.all:
            val = self._constraints.get_value(name)
            return 999 if val is None else val
        else:
            return 999

    def update_tracked(self):
        pass


class WillmottHorizontalCalculator(HklCalculatorBase):

    def __init__(self, ubcalc, constraints,
                 raiseExceptionsIfAnglesDoNotMapBackToHkl=True):
        """"
        Where constraints.reference is a one element dict with the key either
        ('betain', 'betaout' or 'equal') and the value a number or None for
        'betain_eq_betaout'
        """

        HklCalculatorBase.__init__(self, ubcalc,
                                   raiseExceptionsIfAnglesDoNotMapBackToHkl)

        if constraints is not None:
            self.constraints = constraints
            self.parameter_manager = ConstraintAdapter(constraints)
        else:
            self.constraints = DummyConstraints()
            self.parameter_manager = DummyParameterManager()

    @property
    def _UB(self):
        return self._ubcalc.UB

    def _anglesToHkl(self, pos, wavelength):
        """
        Calculate miller indices from position in radians.
        """
        hkl_matrix = angles_to_hkl(pos.delta, pos.gamma, pos.omegah, pos.phi,
                             wavelength, self._UB)
        return hkl_matrix[0, 0], hkl_matrix[1, 0], hkl_matrix[2, 0],

    def _anglesToVirtualAngles(self, pos, wavelength):
        """
        Calculate virtual-angles in radians from position in radians.

        Return theta, alpha, and beta in a dictionary.
        """

        betain = pos.omegah                                              # (52)

        hkl = angles_to_hkl(pos.delta, pos.gamma, pos.omegah, pos.phi,
                              wavelength, self._UB)
        H_phi = self._UB * hkl
        H_phi = H_phi / (2 * pi / wavelength)
        l_phi = H_phi[2, 0]
        sin_betaout = l_phi - sin(betain)
        betaout = asin(bound(sin_betaout))                               # (54)

        cos_2theta = cos(pos.delta) * cos(pos.gamma)
        theta = acos(bound(cos_2theta)) / 2.

        return {'theta': theta, 'betain': betain, 'betaout': betaout}

    def _hklToAngles(self, h, k, l, wavelength):
        """
        Calculate position and virtual angles in radians for a given hkl.
        """

        H_phi = self._UB * matrix([[h], [k], [l]])  # units: 1/Angstrom
        H_phi = H_phi / (2 * pi / wavelength)       # units: 2*pi/wavelength
        h_phi = H_phi[0, 0]
        k_phi = H_phi[1, 0]
        l_phi = H_phi[2, 0]                                               # (5)

        ### determine betain (omegah) and betaout ###

        if not self.constraints.reference:
            raise ValueError("No reference constraint has been constrained.")

        ref_name, ref_value = self.constraints.reference.items()[0]
        if ref_value is not None:
            ref_value *= TORAD
        if ref_name == 'betain':
            betain = ref_value
            betaout = asin(bound(l_phi - sin(betain)))                   # (53)
        elif ref_name == 'betaout':
            betaout = ref_value
            betain = asin(bound(l_phi - sin(betaout)))                   # (54)
        elif ref_name == 'bin_eq_bout':
            betain = betaout = asin(bound(l_phi / 2))                    # (55)
        else:
            raise ValueError("Unexpected constraint name'%s'." % ref_name)

        if abs(betain) < SMALL:
            raise DiffcalcException('required betain was 0 degrees (requested '
                                    'q is perpendicular to surface normal)')
        if betain < -SMALL:
            raise DiffcalcException("betain was -ve (%.4f)" % betain)
#        logger.info('betain = %.4f, betaout = %.4f',
#                    betain * TODEG, betaout * TODEG)
        omegah = betain                                                  # (52)

        ### determine H_lab (X, Y and Z) ###

        Y = -(h_phi ** 2 + k_phi ** 2 + l_phi ** 2) / 2                  # (45)

        Z = (sin(betaout) + sin(betain) * (Y + 1)) / cos(omegah)         # (47)

        X_squared = (h_phi ** 2 + k_phi ** 2 -
                    ((cos(betain) * Y + sin(betain) * Z) ** 2))          # (48)
        if (X_squared < 0) and (abs(X_squared) < SMALL):
            X_squared = 0
        Xpositive = sqrt(X_squared)
        if CHOOSE_POSITIVE_GAMMA:
            X = -Xpositive
        else:
            X = Xpositive
#        logger.info('H_lab (X,Y,Z) = [%.4f, %.4f, %.4f]', X, Y, Z)
        ### determine diffractometer angles ###

        gamma = atan2(-X, Y + 1)                                         # (49)
        if (abs(gamma) < SMALL):
            # degenerate case, only occurs when q || z
            delta = 2 * omegah
        else:
            delta = atan2(Z * sin(gamma), -X)                            # (50)
        M = cos(betain) * Y + sin(betain) * Z
        phi = atan2(h_phi * M - k_phi * X, h_phi * X + k_phi * M)        # (51)

        pos = WillmottHorizontalPosition(delta, gamma, omegah, phi)
        virtual_angles = {'betain': betain, 'betaout': betaout}
        return pos, virtual_angles
