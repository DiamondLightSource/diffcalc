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

from math import pi

from diffcalc.util import AbstractPosition

TORAD = pi / 180
TODEG = 180 / pi
from diffcalc.util import x_rotation, z_rotation, y_rotation

from diffcalc.hkl.you.constraints import NUNAME

class YouGeometry(object):

    def __init__(self, name, fixed_constraints ):
        self.name = name
        self.fixed_constraints = fixed_constraints

    def physical_angles_to_internal_position(self, physicalAngles):
        raise NotImplementedError()

    def internal_position_to_physical_angles(self, physicalAngles):
        raise NotImplementedError()

    def create_position(self, *args):
        return YouPosition(*args)


#==============================================================================
#==============================================================================
# Geometry plugins for use with 'You' hkl calculation engine
#==============================================================================
#==============================================================================


class SixCircle(YouGeometry):
    def __init__(self):
        YouGeometry.__init__(self, 'sixc', {})

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        return YouPosition(*physical_angle_tuple)

    def internal_position_to_physical_angles(self, internal_position):
        return internal_position.totuple()


class FourCircle(YouGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self):
        YouGeometry.__init__(self, 'fourc', {'mu': 0, NUNAME: 0})

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta, eta, chi, phi = physical_angle_tuple
        return YouPosition(0, delta, 0, eta, chi, phi)

    def internal_position_to_physical_angles(self, internal_position):
        _, delta, _, eta, chi, phi = internal_position.totuple()
        return delta, eta, chi, phi

#==============================================================================


def create_you_matrices(mu=None, delta=None, nu=None, eta=None, chi=None,
                        phi=None):
    """
    Create transformation matrices from H. You's paper.
    """
    MU = None if mu is None else calcMU(mu)
    DELTA = None if delta is None else calcDELTA(delta)
    NU = None if nu is None else calcNU(nu)
    ETA = None if eta is None else calcETA(eta)
    CHI = None if chi is None else calcCHI(chi)
    PHI = None if phi is None else calcPHI(phi)
    return MU, DELTA, NU, ETA, CHI, PHI


def calcNU(nu):
    return x_rotation(nu)


def calcDELTA(delta):
    return z_rotation(-delta)


def calcMU(mu_or_alpha):
    return x_rotation(mu_or_alpha)


def calcETA(eta):
    return z_rotation(-eta)


def calcCHI(chi):
    return y_rotation(chi)


def calcPHI(phi):
    return z_rotation(-phi)


class YouPosition(AbstractPosition):

    def __init__(self, mu=None, delta=None, nu=None, eta=None, chi=None,
                 phi=None):
        self.mu = mu
        self.delta = delta
        self.nu = nu
        self.eta = eta
        self.chi = chi
        self.phi = phi

    def clone(self):
        return YouPosition(self.mu, self.delta, self.nu, self.eta, self.chi,
                           self.phi)

    def changeToRadians(self):
        self.mu *= TORAD
        self.delta *= TORAD
        self.nu *= TORAD
        self.eta *= TORAD
        self.chi *= TORAD
        self.phi *= TORAD

    def changeToDegrees(self):
        self.mu *= TODEG
        self.delta *= TODEG
        self.nu *= TODEG
        self.eta *= TODEG
        self.chi *= TODEG
        self.phi *= TODEG

    def totuple(self):
        return (self.mu, self.delta, self.nu, self.eta, self.chi, self.phi)

    def __str__(self):
        return ("YouPosition(mu %r delta: %r nu: %r eta: %r chi: %r  phi: %r)"
                % self.totuple())
    
    def __eq__(self, other):
        return self.totuple() == other.totuple()
