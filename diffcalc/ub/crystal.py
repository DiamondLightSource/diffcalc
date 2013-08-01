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

from math import pi, cos, sin, acos, sqrt

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

TORAD = pi / 180
TODEG = 180 / pi


class CrystalUnderTest(object):
    """
    Contains the lattice parameters and calculated B matrix for the crytsal
    under test. Also Calculates the distance between planes at a given hkl
    value.

    The lattice paraemters can be specified and then if desired saved to a
    __library to be loaded later. The parameters are persisted across restarts.
    Lattices stored in config/var/crystals.xml .
    """

    def __init__(self, name, a, b, c, alpha, beta, gamma):
        '''Creates a new lattice and calculates related values.

        Keyword arguments:
            name -- a string
            a,b,c,alpha,beta,gamma -- lengths and angles (in degrees)
        '''

        self._name = name

        # Set the direct lattice parameters
        self._a1 = a1 = a
        self._a2 = a2 = b
        self._a3 = a3 = c
        self._alpha1 = alpha1 = alpha * TORAD
        self._alpha2 = alpha2 = beta * TORAD
        self._alpha3 = alpha3 = gamma * TORAD

        # Calculate the reciprocal lattice parameters
        self._beta1 = acos((cos(alpha2) * cos(alpha3) - cos(alpha1)) /
                           (sin(alpha2) * sin(alpha3)))

        self._beta2 = beta2 = acos((cos(alpha1) * cos(alpha3) - cos(alpha2)) /
                                   (sin(alpha1) * sin(alpha3)))

        self._beta3 = beta3 = acos((cos(alpha1) * cos(alpha2) - cos(alpha3)) /
                                   (sin(alpha1) * sin(alpha2)))

        volume = (a1 * a2 * a3 *
                  sqrt(1 + 2 * cos(alpha1) * cos(alpha2) * cos(alpha3) -
                       cos(alpha1) ** 2 - cos(alpha2) ** 2 - cos(alpha3) ** 2))

        self._b1 = b1 = 2 * pi * a2 * a3 * sin(alpha1) / volume
        self._b2 = b2 = 2 * pi * a1 * a3 * sin(alpha2) / volume
        self._b3 = b3 = 2 * pi * a1 * a2 * sin(alpha3) / volume

        # Calculate the BMatrix from the direct and reciprical parameters.
        # Reference: Busang and Levy (1967)
        self._bMatrix = matrix([
            [b1, b2 * cos(beta3), b3 * cos(beta2)],
            [0.0, b2 * sin(beta3), -b3 * sin(beta2) * cos(alpha1)],
            [0.0, 0.0, 2 * pi / a3]])

    @property
    def B(self):
        '''
        Returns the B matrix, may be null if crystal is not set, or if there
        was a problem calculating this'''
        return self._bMatrix

    def get_hkl_plane_distance(self, hkl):
        '''Calculates and returns the distance between planes'''
        h, k, l = hkl
        c1 = self._a1 * self._a2 * cos(self._beta3)
        c2 = self._a1 * self._a3 * cos(self._beta2)
        c3 = self._a2 * self._a3 * cos(self._beta1)
        return sqrt(1.0 / (h ** 2 * self._a1 ** 2 + k ** 2 * self._a2 ** 2 +
                           l ** 2 * self._a3 ** 2 + 2 * h * k * c1 +
                           2 * h * l * c2 + 2 * k * l * c3))

    def __str__(self):
        '''    Returns lattice name and all set and calculated parameters'''
        return '\n'.join(self.str_lines())

    def str_lines(self):
        WIDTH = 13
        if self._name is None:
            return ["   none specified"]

        b = self._bMatrix
        lines = []
        lines.append("   name:".ljust(WIDTH) + self._name.rjust(9))
        lines.append("")
        lines.append("   a, b, c:".ljust(WIDTH) +
                     "% 9.5f % 9.5f % 9.5f" % (self.getLattice()[1:4]))
        lines.append(" " * WIDTH +
                     "% 9.5f % 9.5f % 9.5f" % (self.getLattice()[4:]))
        lines.append("")

        fmt = "% 9.5f % 9.5f % 9.5f"
        lines.append("   B matrix:".ljust(WIDTH) +
                     fmt % (b[0, 0], b[0, 1], b[0, 2]))
        lines.append(' ' * WIDTH + fmt % (b[1, 0], b[1, 1], b[1, 2]))
        lines.append(' ' * WIDTH + fmt % (b[2, 0], b[2, 1], b[2, 2]))
        return lines

    def getLattice(self):
        return(self._name, self._a1, self._a2, self._a3, self._alpha1 * TODEG,
               self._alpha2 * TODEG, self._alpha3 * TODEG)

