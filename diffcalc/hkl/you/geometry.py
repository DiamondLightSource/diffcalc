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

from diffcalc.util import AbstractPosition, DiffcalcException
from diffcalc import settings

TORAD = pi / 180
TODEG = 180 / pi
from diffcalc.util import x_rotation, z_rotation, y_rotation

from diffcalc.settings import NUNAME

class YouGeometry(object):

    def __init__(self, name, fixed_constraints, beamline_axes_transform=None):
        self.name = name
        self.fixed_constraints = fixed_constraints
        # beamline_axes_transform matrix is composed of columns of the
        # beamline basis vector coordinates in the diffcalc coordinate system,
        # i.e. it transforms the beamline coordinate system into the diffcalc one.
        self.beamline_axes_transform = beamline_axes_transform

    def map_to_internal_position(self, name, value):
        return name, value

    def map_to_external_position(self, name, value):
        return name, value

    def map_to_internal_name(self, name):
        return name

    def map_to_external_name(self, name):
        return name

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        raise NotImplementedError()

    def internal_position_to_physical_angles(self, internal_position):
        raise NotImplementedError()

    def create_position(self, *args):
        return YouPosition(*args, unit='DEG')


class YouRemappedGeometry(YouGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self, name, fixed_constraints, beamline_axes_transform=None):
        YouGeometry.__init__(self, name, fixed_constraints, beamline_axes_transform)

        # Order should match scannable order in _fourc group for mapping to work correctly
        self._scn_mapping_to_int = ()
        self._scn_mapping_to_ext = ()

    def map_to_internal_name(self, name):
        scn_names = settings.hardware.diffhw.getInputNames()
        try:
            idx_name = scn_names.index(name)
            you_name, _ = self._scn_mapping_to_int[idx_name]
            return you_name
        except ValueError:
            return name

    def map_to_external_name(self, name):
        scn_names = settings.hardware.diffhw.getInputNames()
        for idx, (you_name, _) in enumerate(self._scn_mapping_to_ext):
            if you_name == name:
                return scn_names[idx]
        return name

    def map_to_internal_position(self, name, value):
        scn_names = settings.hardware.diffhw.getInputNames()
        try:
            idx_name = scn_names.index(name)
        except ValueError:
            return name, value
        new_name, op = self._scn_mapping_to_int[idx_name]
        try:
            return new_name, op(value)
        except TypeError:
            return new_name, None

    def map_to_external_position(self, name, value):
        try:
            (idx, _, op), = tuple((i, nm, o) for i, (nm, o) in enumerate(self._scn_mapping_to_ext) if nm == name)
        except ValueError:
            return name, value
        scn_names = settings.hardware.diffhw.getInputNames()
        try:
            ext_name = scn_names[idx]
        except ValueError:
            return name, value
        try:
            return ext_name, op(value)
        except TypeError:
            return ext_name, None

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        you_angles = {}
        scn_names = settings.hardware.diffhw.getInputNames()
        for scn_name, phys_angle in zip(scn_names, physical_angle_tuple):
            name, val = self.map_to_internal_position(scn_name, phys_angle)
            you_angles[name] = val
        you_angles.update(self.fixed_constraints)

        angle_values = tuple(you_angles[name] for name in YouPosition.get_names())
        return YouPosition(*angle_values, unit='DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        you_angles = clone_position.todict()
        res = []
        for name, _ in self._scn_mapping_to_ext:
            _, val = self.map_to_external_position(name, you_angles[name])
            res.append(val)
        return tuple(res)

#==============================================================================
#==============================================================================
# Geometry plugins for use with 'You' hkl calculation engine
#==============================================================================
#==============================================================================


class SixCircle(YouGeometry):
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'sixc', {}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        return YouPosition(*physical_angle_tuple, unit='DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        return clone_position.totuple()


class FourCircle(YouGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'fourc', {'mu': 0, NUNAME: 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta, eta, chi, phi = physical_angle_tuple
        return YouPosition(0, delta, 0, eta, chi, phi, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        _, delta, _, eta, chi, phi = clone_position.totuple()
        return delta, eta, chi, phi


class FiveCircle(YouGeometry):
    """For a diffractometer with angles:
          delta, nu, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'fivec', {'mu': 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta, nu, eta, chi, phi = physical_angle_tuple
        return YouPosition(0, delta, nu, eta, chi, phi, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        _, delta, nu, eta, chi, phi = clone_position.totuple()
        return delta, nu, eta, chi, phi


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

    def __init__(self, mu, delta, nu, eta, chi, phi, unit):
        self.mu = mu
        self.delta = delta
        self.nu = nu
        self.eta = eta
        self.chi = chi
        self.phi = phi
        if unit not in ['DEG', 'RAD']:
            raise DiffcalcException("Invalid angle unit value %s." % str(unit))
        else:
            self.unit = unit

    def clone(self):
        return YouPosition(self.mu, self.delta, self.nu, self.eta, self.chi,
                           self.phi, self.unit)

    def changeToRadians(self):
        if self.unit == 'DEG':
            self.mu *= TORAD
            self.delta *= TORAD
            self.nu *= TORAD
            self.eta *= TORAD
            self.chi *= TORAD
            self.phi *= TORAD
            self.unit = 'RAD'
        elif self.unit == 'RAD':
            return
        else:
            raise DiffcalcException("Invalid angle unit value %s." % str(self.unit))

    def changeToDegrees(self):
        if self.unit == 'RAD':
            self.mu *= TODEG
            self.delta *= TODEG
            self.nu *= TODEG
            self.eta *= TODEG
            self.chi *= TODEG
            self.phi *= TODEG
            self.unit = 'DEG'
        elif self.unit == 'DEG':
            return
        else:
            raise DiffcalcException("Invalid angle unit value %s." % str(self.unit))

    @staticmethod
    def get_names():
        return ('mu', 'delta', NUNAME, 'eta', 'chi', 'phi')

    def totuple(self):
        return (self.mu, self.delta, self.nu, self.eta, self.chi, self.phi)

    def todict(self):
        return dict(zip(self.get_names(), self.totuple()))

    def __str__(self):
        fmt_tuple = sum(zip(self.get_names(), self.totuple()), ()) + (self.unit,)
        return ("YouPosition(%s: %r %s: %r %s: %r %s: %r %s: %r  %s: %r) in %s"
                % fmt_tuple)
    
    def __eq__(self, other):
        return self.totuple() == other.totuple()


class WillmottHorizontalPosition(YouPosition):

    def __init__(self, delta=None, gamma=None, omegah=None, phi=None):
        self.mu = 0
        self.delta = delta
        self.nu = gamma
        self.eta = omegah
        self.chi = -90
        self.phi = phi
        self.unit= 'DEG'
