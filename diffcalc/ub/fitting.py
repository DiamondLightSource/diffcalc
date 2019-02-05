###one,
# Copyright 2008-2019 Diamond Light Source Ltd.
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
from diffcalc.util import DiffcalcException, SMALL, angle_between_vectors, TODEG
from math import pi, sqrt, sin, cos, atan2
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.hkl.you.geometry import create_you_matrices

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm


def is_small(x):
    return abs(x) < SMALL


def sign(x):
    if is_small(x):
        return 0
    if x > 0:
        return 1
    # x < 0
    return -1


def _get_refl_hkl(refl_list):
    refl_data = []
    for ref in refl_list:
        hkl_vals, pos, en = ref
        refl_data.append((matrix([hkl_vals]).T, pos, en))
    return refl_data


def _func_crystal(vals, uc_system, ref_data):
    trial_cr = CrystalUnderTest('trial', uc_system, 1, 1, 1, 90, 90, 90)
    try:
        trial_cr._set_cell_for_system(uc_system, *vals)
    except Exception:
        return 1e6

    res = 0
    I = matrix('1 0 0; 0 1 0; 0 0 1')
    for (hkl_vals, pos_vals, en) in ref_data:
        wl = 12.3984 / en
        [_, DELTA, NU, _, _, _] = create_you_matrices(*pos_vals.totuple())
        q_pos = (NU * DELTA - I) * matrix([[0], [2 * pi / wl], [0]])
        q_hkl = trial_cr.B * hkl_vals
        res += (norm(q_pos) - norm(q_hkl))**2
    return res


class UbTargetCrystal(object):

    def __init__(self, refl_list, uc_system):
        self.uc_system = uc_system
        self.ref_data = _get_refl_hkl(refl_list)

    def value(self, vals):
        return _func_crystal(vals, self.uc_system, self.ref_data)


def _func_orient(vals, crystal, ref_data):
    quat = _get_quat_from_u123(*vals)
    trial_u = _get_rot_matrix(*quat)
    tmp_ub = trial_u * crystal.B

    res = 0
    I = matrix('1 0 0; 0 1 0; 0 0 1')
    for (hkl_vals, pos_vals, en) in ref_data:
        wl = 12.3984 / en
        [MU, DELTA, NU, ETA, CHI, PHI] = create_you_matrices(*pos_vals.totuple())
        q_del = (NU * DELTA - I) * matrix([[0], [2 * pi / wl], [0]])
        q_vals = PHI.I * CHI.I * ETA.I * MU.I * q_del

        q_hkl = tmp_ub * hkl_vals
        res += angle_between_vectors(q_hkl, q_vals)
    return res


class UbTargetOrient(object):

    def __init__(self, refl_list, crystal):
        self.crystal = crystal
        self.ref_data = _get_refl_hkl(refl_list)

    def value(self, vals):
        return _func_orient(vals, self.crystal, self.ref_data)


def get_crystal_target(refl_list, system):

    try:
        from org.apache.commons.math3.analysis import MultivariateFunction
        from org.apache.commons.math3.optim.nonlinear.scalar import ObjectiveFunction

        class MultivariateFunctionUbTarget(MultivariateFunction):

            def value(self, vals):
                target_obj = UbTargetCrystal(refl_list, system)
                return target_obj.value(vals)

        return ObjectiveFunction(MultivariateFunctionUbTarget())
    except ImportError:
        target_obj = UbTargetCrystal(refl_list, system)
        return target_obj.value


def get_u_target(refl_list, crystal):

    try:
        from org.apache.commons.math3.analysis import MultivariateFunction
        from org.apache.commons.math3.optim.nonlinear.scalar import ObjectiveFunction

        class MultivariateFunctionUbTarget(MultivariateFunction):

            def value(self, vals):
                target_obj = UbTargetOrient(refl_list, crystal)
                return target_obj.value(vals)

        return ObjectiveFunction(MultivariateFunctionUbTarget())
    except ImportError:
        target_obj = UbTargetOrient(refl_list, crystal)
        return target_obj.value


def _get_rot_matrix(q0, q1, q2, q3):
    rot = matrix([[q0**2 + q1**2 - q2**2 - q3**2,            2.*(q1*q2 - q0*q3),            2.*(q1*q3 + q0*q2),],
                  [           2.*(q1*q2 + q0*q3), q0**2 - q1**2 + q2**2 - q3**2,            2.*(q2*q3 - q0*q1),],
                  [           2.*(q1*q3 - q0*q2),            2.*(q2*q3 + q0*q1), q0**2 - q1**2 - q2**2 + q3**2,]])
    return rot


def _get_init_u123(um):

    tr = um[0,0] + um[1,1] + um[2,2]
    sgn_q1 = sign(um[2,1] - um[1,2])
    sgn_q2 = sign(um[0,2] - um[2,0])
    sgn_q3 = sign(um[1,0] - um[0,1])
    q0 = sqrt(1. + tr) / 2.
    q1 = sgn_q1 * sqrt(1. + um[0,0] - um[1,1] - um[2,2]) / 2.0
    q2 = sgn_q2 * sqrt(1. - um[0,0] + um[1,1] - um[2,2]) / 2.0
    q3 = sgn_q3 * sqrt(1. - um[0,0] - um[1,1] + um[2,2]) / 2.0
    u1 = (1. - um[0,0]) / 2.
    u2 = atan2(q0, q1) / (2. * pi)
    u3 = atan2(q2, q3) / (2. * pi)
    if u2 < 0: u2 += 1.
    if u3 < 0: u3 += 1.
    return u1, u2, u3


def _get_quat_from_u123(u1, u2, u3):
    q0, q1 = sqrt(1.-u1)*sin(2.*pi*u2), sqrt(1.-u1)*cos(2.*pi*u2)
    q2, q3 =    sqrt(u1)*sin(2.*pi*u3),    sqrt(u1)*cos(2.*pi*u3)
    return q0, q1, q2, q3


def _get_uc_upper_limits(system):
    max_unit = 100.
    sgm_unit = 1e-2
    sgm_angle = 1e-1
    if system == 'Triclinic':
        return ([max_unit, max_unit, max_unit,
                    180., 180., 180.],
                [sgm_unit, sgm_unit, sgm_unit,
                    sgm_angle, sgm_angle, sgm_angle])
    elif system == 'Monoclinic':
        return ([max_unit, max_unit, max_unit, 180.],
                [sgm_unit, sgm_unit, sgm_unit, sgm_angle])
    elif system == 'Orthorhombic':
        return ([max_unit, max_unit, max_unit,],
                [sgm_unit, sgm_unit, sgm_unit,])
    elif system == 'Tetragonal' or system == 'Hexagonal':
        return ([max_unit, max_unit,],
                [sgm_unit, sgm_unit,])
    elif system == 'Rhombohedral': 
        return ([max_unit, 180.,],
                [sgm_unit, sgm_angle,])
    elif system == 'Cubic':
        return ([max_unit,],
                [sgm_unit,])
    else:
        raise TypeError("Invalid crystal system parameter: %s" % str(system))


def fit_crystal(uc, refl_list):
    try:
        uc_system, uc_params = uc.get_lattice_params()
        start = uc_params
        lower = [0,] * len(uc_params)
        upper, sigma = _get_uc_upper_limits(uc_system)
    except AttributeError:
        raise DiffcalcException("UB matrix not initialised. Cannot run UB matrix fitting procedure.")
    try:
        from org.apache.commons.math3.optim.nonlinear.scalar.noderiv import CMAESOptimizer
        from org.apache.commons.math3.optim.nonlinear.scalar import GoalType
        from org.apache.commons.math3.optim import MaxEval, InitialGuess, SimpleBounds
        from org.apache.commons.math3.random import MersenneTwister
        
        optimizer = CMAESOptimizer(30000,
                                   0,
                                   True,
                                   10,
                                   0,
                                   MersenneTwister(),
                                   True,
                                   None)
        opt = optimizer.optimize((MaxEval(5000),
                                   get_crystal_target(refl_list, uc_system),
                                   GoalType.MINIMIZE,
                                   CMAESOptimizer.PopulationSize(15),
                                   CMAESOptimizer.Sigma(sigma),
                                   InitialGuess(start),
                                   SimpleBounds(lower, upper)))
        vals = opt.getPoint()
        #res = opt.getValue()
    except ImportError:
        from scipy.optimize import minimize

        ref_data = _get_refl_hkl(refl_list)
        bounds = zip(lower, upper)
        res = minimize(_func_crystal,
                       start,
                       args=(uc_system, ref_data),
                       method='SLSQP',
                       tol=1e-10,
                       options={'disp' : False,
                                'maxiter': 10000,
                                'eps': 1e-6,
                                'ftol': 1e-10},
                       bounds=bounds)
        vals = res.x
    res_cr = CrystalUnderTest('trial', uc_system, 1, 1, 1, 90, 90, 90)
    res_cr._set_cell_for_system(uc_system, *vals)
    return res_cr

def fit_u_matrix(init_u, uc, refl_list):
    try:
        start = list(_get_init_u123(init_u))
        lower = [ 0, 0, 0]
        upper = [ 1, 1, 1]
        sigma = [ 1e-2, 1e-2, 1e-2]
    except AttributeError:
        raise DiffcalcException("UB matrix not initialised. Cannot run UB matrix fitting procedure.")
    try:
        from org.apache.commons.math3.optim.nonlinear.scalar.noderiv import CMAESOptimizer
        from org.apache.commons.math3.optim.nonlinear.scalar import GoalType
        from org.apache.commons.math3.optim import MaxEval, InitialGuess, SimpleBounds
        from org.apache.commons.math3.random import MersenneTwister
        
        optimizer = CMAESOptimizer(30000,
                                   0,
                                   True,
                                   10,
                                   0,
                                   MersenneTwister(),
                                   True,
                                   None)
        opt = optimizer.optimize((MaxEval(3000),
                                   get_u_target(refl_list, uc),
                                   GoalType.MINIMIZE,
                                   CMAESOptimizer.PopulationSize(15),
                                   CMAESOptimizer.Sigma(sigma),
                                   InitialGuess(start),
                                   SimpleBounds(lower, upper)))
        vals = opt.getPoint()
        res = opt.getValue()
    except ImportError:
        from scipy.optimize import minimize

        ref_data = _get_refl_hkl(refl_list)
        bounds = zip(lower, upper)
        res = minimize(_func_orient,
                       start,
                       args=(uc, ref_data),
                       method='SLSQP',
                       tol=1e-10,
                       options={'disp' : False,
                                'maxiter': 10000,
                                'eps': 1e-6,
                                'ftol': 1e-10},
                       bounds=bounds)
        vals = res.x
    q0, q1, q2, q3 = _get_quat_from_u123(*vals)
    res_u = _get_rot_matrix(q0, q1, q2, q3)
    #angle = 2. * acos(q0)
    #xr = q1 / sqrt(1. - q0 * q0)
    #yr = q2 / sqrt(1. - q0 * q0)
    #zr = q3 / sqrt(1. - q0 * q0)
    #print angle * TODEG, (xr, yr, zr), res
    return res_u
