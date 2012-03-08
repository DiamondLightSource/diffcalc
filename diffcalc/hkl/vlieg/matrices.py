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

from math import cos, sin

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.util import x_rotation, z_rotation, y_rotation


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
