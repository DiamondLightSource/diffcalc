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

from math import pi, sin, cos, acos, asin, atan2, sqrt
from itertools import product

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm

from diffcalc.log import logging
from diffcalc.hkl.calcbase import HklCalculatorBase
from diffcalc.hkl.you.geometry import create_you_matrices, calcMU, calcPHI, \
    calcCHI, calcETA
from diffcalc.hkl.you.geometry import YouPosition
from diffcalc.util import DiffcalcException, bound, angle_between_vectors,\
    y_rotation
from diffcalc.util import cross3, z_rotation, x_rotation
from diffcalc.ub.calc import PaperSpecificUbCalcStrategy

from diffcalc.hkl.you.constraints import NUNAME
logger = logging.getLogger("diffcalc.hkl.you.calc")
I = matrix('1 0 0; 0 1 0; 0 0 1')
y = matrix('0; 1; 0')

SMALL = 1e-6
TORAD = pi / 180
TODEG = 180 / pi

PRINT_DEGENERATE = False


def is_small(x):
    return abs(x) < SMALL


def sign(x):
    if x == 0:
        return 0
    if x > 0:
        return 1
    # x < 0
    return -1


def normalised(vector):
    return vector * (1 / norm(vector))


def cut_at_minus_pi(value):
    if value < (-pi - SMALL):
        return value + 2 * pi
    if value >= pi + SMALL:
        return value - 2 * pi
    return value


def _calc_N(Q, n):
    """Return N as described by Equation 31"""
    Q = normalised(Q)
    n = normalised(n)
    if is_small(angle_between_vectors(Q, n)):
        raise DiffcalcException('Q and n are parallel and cannot be used to create '
                         'an orthonormal matrix')
    Qxn = cross3(Q, n)
    QxnxQ = cross3(Qxn, Q)
    QxnxQ = normalised(QxnxQ)
    Qxn = normalised(Qxn)
    return matrix([[Q[0, 0], QxnxQ[0, 0], Qxn[0, 0]],
                   [Q[1, 0], QxnxQ[1, 0], Qxn[1, 0]],
                   [Q[2, 0], QxnxQ[2, 0], Qxn[2, 0]]])


def _calc_angle_between_naz_and_qaz(theta, alpha, tau):
    # Equation 30:
    top = cos(tau) - sin(alpha) * sin(theta)
    bottom = cos(alpha) * cos(theta)
    if is_small(bottom):
        if is_small(cos(alpha)):
            raise ValueError('cos(alpha) is too small')
        if is_small(cos(theta)):
            raise ValueError('cos(theta) is too small')
    if is_small(sin(tau)):
        return 0.
    return acos(bound(top / bottom))


def youAnglesToHkl(pos, wavelength, UBmatrix):
    """Calculate miller indices from position in radians.
    """

    [MU, DELTA, NU, ETA, CHI, PHI] = create_you_matrices(*pos.totuple())

    q_lab = (NU * DELTA - I) * matrix([[0], [2 * pi / wavelength], [0]])   # 12

    hkl = UBmatrix.I * PHI.I * CHI.I * ETA.I * MU.I * q_lab

    return hkl[0, 0], hkl[1, 0], hkl[2, 0]


def _tidy_degenerate_solutions(pos, constraints):

    original = pos.inDegrees()
    detector_like_constraint = constraints.detector or constraints.naz
    nu_constrained_to_0 = is_small(pos.nu) and detector_like_constraint
    mu_constrained_to_0 = is_small(pos.mu) and 'mu' in constraints.sample
    delta_constrained_to_0 = is_small(pos.delta) and detector_like_constraint
    eta_constrained_to_0 = is_small(pos.eta) and 'eta' in constraints.sample
    phi_not_constrained = not 'phi' in constraints.sample

    if nu_constrained_to_0 and mu_constrained_to_0 and phi_not_constrained:
        # constrained to vertical 4-circle like mode
        if is_small(pos.chi):  # phi || eta
            desired_eta = pos.delta / 2.
            eta_diff = desired_eta - pos.eta
            pos.eta = desired_eta
            pos.phi -= eta_diff
            if PRINT_DEGENERATE:
                print ('DEGENERATE: with chi=0, phi and eta are colinear:'
                       'choosing eta = delta/2 by adding % 7.3f to eta and '
                       'removing it from phi. (mu=%s=0 only)' % (eta_diff * TODEG, NUNAME))
                print '            original:', original

    elif delta_constrained_to_0 and eta_constrained_to_0 and phi_not_constrained:
        # constrained to horizontal 4-circle like mode
        if is_small(pos.chi - pi / 2):  # phi || mu
            desired_mu = pos.nu / 2.
            mu_diff = desired_mu - pos.mu
            pos.mu = desired_mu
            pos.phi += mu_diff
            if PRINT_DEGENERATE:
                print ('DEGENERATE: with chi=90, phi and mu are colinear: choosing'
                       ' mu = %s/2 by adding % 7.3f to mu and to phi. '
                       '(delta=eta=0 only)' % (NUNAME, mu_diff * TODEG))
                print '            original:', original

    return pos


def _theta_and_qaz_from_detector_angles(delta, nu):
    # Equation 19:
    cos_2theta = cos(delta) * cos(nu)
    theta = acos(bound(cos_2theta)) / 2.
    sgn = sign(sin(2. * theta))
    qaz = atan2(sgn * sin(delta), sgn * cos(delta) * sin(nu))
    return theta, qaz


class YouUbCalcStrategy(PaperSpecificUbCalcStrategy):

    def calculate_q_phi(self, pos):

        [MU, DELTA, NU, ETA, CHI, PHI] = create_you_matrices(*pos.totuple())
        # Equation 12: Compute the momentum transfer vector in the lab  frame
        q_lab = (NU * DELTA - I) * y
        # Transform this into the phi frame.
        return PHI.I * CHI.I * ETA.I * MU.I * q_lab


UNREACHABLE_MSG = (
    'The current combination of constraints with %s = %.4f\n'
    'prohibits a solution for the specified reflection.')


class YouHklCalculator(HklCalculatorBase):

    def __init__(self, ubcalc, geometry, hardware, constraints,
                  raiseExceptionsIfAnglesDoNotMapBackToHkl=True):
        HklCalculatorBase.__init__(self, ubcalc, geometry, hardware,
                                   raiseExceptionsIfAnglesDoNotMapBackToHkl)
        self._hardware = hardware  # for checking limits only
        self.constraints = constraints
        self.parameter_manager = constraints  # TODO: remove need for this attr

    def __str__(self):
        return self.constraints.__str__()

    def _get_n_phi(self):
        return self._ubcalc.n_phi
    
    def _get_ubmatrix(self):
        return self._getUBMatrix()  # for consistency

    def repr_mode(self):
        return repr(self.constraints.all)

    def _anglesToHkl(self, pos, wavelength):
        """Calculate miller indices from position in radians.
        """
        return youAnglesToHkl(pos, wavelength, self._get_ubmatrix())

    def _anglesToVirtualAngles(self, pos, _wavelength):
        """Calculate pseudo-angles in radians from position in radians.

        Return theta, qaz, alpha, naz, tau, psi and beta in a dictionary.

        """

        # depends on surface normal n_lab.
        mu, delta, nu, eta, chi, phi = pos.totuple()

        theta, qaz = _theta_and_qaz_from_detector_angles(delta, nu)      # (19)

        [MU, _, _, ETA, CHI, PHI] = create_you_matrices(mu,
                                           delta, nu, eta, chi, phi)
        Z = MU * ETA * CHI * PHI
        n_lab = Z * self._get_n_phi()
        alpha = asin(bound((-n_lab[1, 0])))
        naz = atan2(n_lab[0, 0], n_lab[2, 0])                            # (20)

        cos_tau = cos(alpha) * cos(theta) * cos(naz - qaz) + \
                  sin(alpha) * sin(theta)
        tau = acos(bound(cos_tau))                                       # (23)

        # Compute Tau using the dot product directly (THIS ALSO WORKS)
#        q_lab = ( (NU * DELTA - I ) * matrix([[0],[1],[0]])
#        norm = norm(q_lab)
#        q_lab = matrix([[1],[0],[0]]) if norm == 0 else q_lab * (1/norm)
#        tau_from_dot_product = acos(bound(dot3(q_lab, n_lab)))

        sin_beta = 2 * sin(theta) * cos(tau) - sin(alpha)
        beta = asin(bound(sin_beta))                                     # (24)

        psi = next(self._calc_psi(alpha, theta, tau, qaz, naz))

        return {'theta': theta, 'qaz': qaz, 'alpha': alpha,
                'naz': naz, 'tau': tau, 'psi': psi, 'beta': beta}


    def _choose_single_solution(self, pos_virtual_angles_pairs_in_degrees):

        if len(pos_virtual_angles_pairs_in_degrees) == 1:
            return pos_virtual_angles_pairs_in_degrees[0]

        absolute_distances = []
        for pos_, _ in pos_virtual_angles_pairs_in_degrees:
            absolute_distances.append(sum([abs(pos_.totuple()[i]) for i in (0, 3, 4, 5)]))

        shortest_solution_index = absolute_distances.index(
            min(absolute_distances))
        pos, virtual_angles = pos_virtual_angles_pairs_in_degrees[shortest_solution_index]

        if logger.isEnabledFor(logging.INFO):
            msg = ('Multiple sample solutions found (choosing solution with '
                   'shortest distance to all-zeros position):\n')
            i = 0
            for (pos_, _), distance in zip(pos_virtual_angles_pairs_in_degrees,
                                          absolute_distances):
                msg += '*' if i == shortest_solution_index else '.'

                msg += ('mu=% 7.3f, delta=% 7.3f, nu=% 7.3f, eta=% 7.3f, chi=% 7.3f, phi=% 7.3f' %
                        pos_.totuple())
                msg += ' (distance=% 4.3f)\n' % (distance * TODEG)
                i += 1
            msg += ':\n'
            logger.info(msg)

        return pos, virtual_angles

    def hklToAngles(self, h, k, l, wavelength, return_all_solutions=False):
        """
        Return verified Position and all virtual angles in degrees from
        h, k & l and wavelength in Angstroms.

        The calculated Position is verified by checking that it maps back using
        anglesToHkl() to the requested hkl value.

        Those virtual angles fixed or generated while calculating the position
        are verified by by checking that they map back using
        anglesToVirtualAngles to the virtual angles for the given position.

        Throws a DiffcalcException if either check fails and
        raiseExceptionsIfAnglesDoNotMapBackToHkl is True, otherwise displays a
        warning.
        """

        pos_virtual_angles_pairs = self._hklToAngles(h, k, l, wavelength, return_all_solutions)  # in rad
        assert pos_virtual_angles_pairs
        pos_virtual_angles_pairs_in_degrees = []
        for pos, virtual_angles in pos_virtual_angles_pairs:
            
            # to degrees:
            pos.changeToDegrees()
            for key, val in virtual_angles.items():
                if val is not None:
                    virtual_angles[key] = val * TODEG

            self._verify_pos_map_to_hkl(h, k, l, wavelength, pos)

            pos_virtual_angles_pairs_in_degrees.append((pos, virtual_angles))

        if return_all_solutions:
            return pos_virtual_angles_pairs_in_degrees
        else:
            pos, virtual_angles = self._choose_single_solution(pos_virtual_angles_pairs_in_degrees)
            return pos, virtual_angles


    def hkl_to_all_angles(self, h, k, l, wavelength):
        return self.hklToAngles(h, k, l, wavelength, True)


    def _hklToAngles(self, h, k, l, wavelength, return_all_solutions=False):
        """(pos, virtualAngles) = hklToAngles(h, k, l, wavelength) --- with
        Position object pos and the virtual angles returned in degrees. Some
        modes may not calculate all virtual angles.
        """

        if not self.constraints.is_fully_constrained():
            raise DiffcalcException(
                "Diffcalc is not fully constrained.\n"
                "Type 'help con' for instructions")

        if not self.constraints.is_current_mode_implemented():
            raise DiffcalcException(
                "Sorry, the selected constraint combination is valid but "
                "is not implemented. Type 'help con' for implemented combinations")
              
        # constraints are dictionaries  
        ref_constraint = self.constraints.reference
        if ref_constraint:
            ref_constraint_name, ref_constraint_value = ref_constraint.items()[0]
        det_constraint = self.constraints.detector
        naz_constraint = self.constraints.naz
        samp_constraints = self.constraints.sample
            
        assert not (det_constraint and naz_constraint), (
               "Two 'detector' constraints given")


        h_phi = self._get_ubmatrix() * matrix([[h], [k], [l]])
        theta = self._calc_theta(h_phi, wavelength)
        tau = angle_between_vectors(h_phi, self._get_n_phi())

        ### Reference constraint column ###

        if ref_constraint:
            # An angle for the reference vector (n) is given      (Section 5.2)         
            alpha, _ = self._calc_remaining_reference_angles(
                ref_constraint_name, ref_constraint_value, theta, tau)

        solution_tuples = []
        if det_constraint or naz_constraint:

            if len(samp_constraints) == 1:
                for qaz, naz, delta, nu in self._calc_det_angles_given_det_or_naz_constraint(
                                                det_constraint, naz_constraint, theta, tau, alpha):
                    delta_nu_pairs = self._filter_angle_limits([(delta, nu),],
                                                               ['delta', NUNAME],
                                                               not return_all_solutions)
                    if not delta_nu_pairs:
                        continue

        
                    for mu, eta, chi, phi in self._calc_sample_angles_from_one_sample_constraint(
                        h, k, l, wavelength, samp_constraints, h_phi, theta,
                        ref_constraint_name, ref_constraint_value, alpha, qaz, naz,
                        delta, nu):
                        solution_tuples.append((mu, delta, nu, eta, chi, phi))

            elif len(samp_constraints) == 2:
                if det_constraint:
                    det_constraint_name, det_constraint_val = det_constraint.items()[0]
                    for delta, nu, qaz in self._calc_remaining_detector_angles(det_constraint_name, det_constraint_val, theta):
                        for mu, eta, chi, phi in self._calc_sample_angles_given_two_sample_and_detector(
                            samp_constraints, qaz, theta, h_phi, self._get_n_phi()):
                            solution_tuples.append((mu, delta, nu, eta, chi, phi))
                
                else:
                    raise DiffcalcException(
                        'No code yet to handle this combination of detector and sample constraints!')

        elif len(samp_constraints) == 2:
            if ref_constraint_name == 'psi':
                psi_vals = [ref_constraint_value,]
            else:
                psi_vals = self._calc_psi(alpha, theta, tau)
            for psi in psi_vals:
                angles = list(self._calc_sample_given_two_sample_and_reference(
                    h, k, l, wavelength, samp_constraints, h_phi, theta,
                    ref_constraint_name, ref_constraint_value, psi))
                solution_tuples.extend(angles)

        elif len(samp_constraints) == 3:
            solution_tuples = self._calc_angles_given_three_sample_constraints(
                h, k, l, wavelength, return_all_solutions, samp_constraints,
                 h_phi, theta)
        
        if not solution_tuples:
            raise DiffcalcException('No solutions were found. '
                'Please consider using an alternative set of constraints.')

        tidy_solutions = [_tidy_degenerate_solutions(YouPosition(*pos, unit='RAD'),
                                                     self.constraints).totuple() for pos in solution_tuples]
        merged_solution_tuples = set(self._filter_angle_limits(tidy_solutions,
                                                      ['mu', 'delta', NUNAME, 'eta', 'chi', 'phi'],
                                                      not return_all_solutions))
        if not merged_solution_tuples:
            raise DiffcalcException('No solutions were found matching existing hardware limits. '
                'Please consider using an alternative set of constraints.')

        #def _find_duplicate_angles(el):
        #    idx, tpl = el
        #    for tmp_tpl in filtered_solutions[idx:]:
        #        if False not in [abs(x-y) < SMALL for x,y in zip(tmp_tpl, tpl)]:
        #            return False
        #    return True
        #merged_solution_tuples = filter(_find_duplicate_angles, enumerate(filtered_solutions, 1))
        position_pseudo_angles_pairs = self._create_position_pseudo_angles_pairs(wavelength, merged_solution_tuples)
        if not position_pseudo_angles_pairs:
            raise DiffcalcException('No solutions were found. Please check hardware limits and '
                'consider using an alternative pseudo-angle constraints.')

        return position_pseudo_angles_pairs


    def _create_position_pseudo_angles_pairs(self, wavelength, merged_solution_tuples):

        position_pseudo_angles_pairs = []
        for pos in merged_solution_tuples:
            # Create position
            position = YouPosition(*pos, unit='RAD')
            #position = _tidy_degenerate_solutions(position, self.constraints)
            #if position.phi <= -pi + SMALL:
            #    position.phi += 2 * pi
            # pseudo angles calculated along the way were for the initial solution
            # and may be invalid for the chosen solution TODO: anglesToHkl need no
            # longer check the pseudo_angles as they will be generated with the
            # same function and it will prove nothing
            pseudo_angles = self._anglesToVirtualAngles(position, wavelength)
            is_sol = True
            for constraint in [self.constraints.reference,
                               self.constraints.detector,
                               self.constraints.naz]:
                try:
                    constraint_name, constraint_value = constraint.items()[0]
                    if constraint_name == 'a_eq_b':
                        if not is_small(pseudo_angles['alpha'] - pseudo_angles['beta']):
                            is_sol = False
                            break
                    #TODO: check that this is an intuitive approach for setting psi constraint
                    #      and possibly needs to be applied to other azimuthal angle constraints
                    elif constraint_name == 'psi':
                        if not is_small(abs(constraint_value) - abs(pseudo_angles[constraint_name])):
                            is_sol = False
                            break
                    else:
                        if not is_small(constraint_value - pseudo_angles[constraint_name]):
                            is_sol = False
                            break
                except:
                    continue
            if is_sol:
                position_pseudo_angles_pairs.append((position, pseudo_angles))
        return position_pseudo_angles_pairs


    def _calc_theta(self, h_phi, wavelength):
        """Calculate theta using Equation1
        """
        q_length = norm(h_phi)
        if q_length == 0:
            raise DiffcalcException('Reflection is unreachable as |Q| is 0')
        wavevector = 2 * pi / wavelength
        try:
            theta = asin(q_length / (2 * wavevector))
        except ValueError:
            raise DiffcalcException(
                'Reflection is unreachable as |Q| is too long')
        return theta

    def _calc_psi(self, alpha, theta, tau, qaz=None, naz=None):
        """Calculate psi from Eq. (18), (25) and (28)
        """
        sin_tau = sin(tau)
        cos_theta = cos(theta)
        if is_small(sin_tau):
            print ('WARNING: Diffcalc could not calculate a unique azimuth '
                   '(psi) as the scattering vector (Q) and the reference '
                   'vector (n) are parallel')
            yield float('Nan')
        elif is_small(cos_theta):
            print ('WARNING: Diffcalc could not calculate a unique azimuth '
                   '(psi) because the scattering vector (Q) and xray beam are '
                   " are parallel and don't form a unique reference plane")
            yield float('Nan')
        else:
            cos_psi = ((cos(tau) * sin(theta) - sin(alpha)) / cos_theta) # (28)
            if qaz is None or naz is None :
                acos_psi = acos(cos_psi / sin_tau)
                for psi in [acos_psi, -acos_psi]:
                    yield psi
            else:
                sin_psi = cos(alpha) * sin(qaz - naz)
                sgn = sign(sin_tau)
                eps = sin_psi**2 + cos_psi**2
                if not is_small(eps/sin_tau**2 - 1):
                    print ('WARNING: Diffcalc could not calculate a unique azimuth '
                           '(psi) because of loss of accuracy in numerical calculation')
                    yield float('Nan')
                else:
                    psi = atan2(sgn * sin_psi, sgn * cos_psi)
                    yield psi


    def _calc_remaining_reference_angles(self, name, value, theta, tau):
        """Return alpha and beta given one of a_eq_b, alpha, beta or psi
        """
        if name == 'psi':
            psi = value
            # Equation 26 for alpha
            sin_alpha = (cos(tau) * sin(theta) -
                         cos(theta) * sin(tau) * cos(psi))
            if abs(sin_alpha) > 1 + SMALL:
                raise DiffcalcException(UNREACHABLE_MSG % (name, value * TODEG))
            alpha = asin(bound(sin_alpha))
            # Equation 27 for beta
            sin_beta = cos(tau) * sin(theta) + cos(theta) * sin(tau) * cos(psi)
            if abs(sin_beta) > 1 + SMALL:
                raise DiffcalcException(UNREACHABLE_MSG % (name, value * TODEG))

            beta = asin(bound(sin_beta))

        elif name == 'a_eq_b':
            alpha = beta = asin(bound(cos(tau) * sin(theta)))            # (24)

        elif name == 'alpha':
            alpha = value                                                # (24)
            sin_beta = 2 * sin(theta) * cos(tau) - sin(alpha)
            if abs(sin_beta) > 1 + SMALL:
                raise DiffcalcException(UNREACHABLE_MSG % (name, value * TODEG))
            beta = asin(sin_beta)

        elif name == 'beta':
            beta = value
            sin_alpha = 2 * sin(theta) * cos(tau) - sin(beta)            # (24)
            if abs(sin_alpha) > 1 + SMALL:
                raise DiffcalcException(UNREACHABLE_MSG % (name, value * TODEG))

            alpha = asin(sin_alpha)

        return alpha, beta

    def _calc_det_angles_given_det_or_naz_constraint(
            self, det_constraint, naz_constraint, theta, tau, alpha):
        
        assert det_constraint or naz_constraint
        naz_qaz_angle = _calc_angle_between_naz_and_qaz(theta, alpha, tau)
        if det_constraint:
            # One of the detector angles is given                 (Section 5.1)
            det_constraint_name, det_constraint = det_constraint.items()[0]
            for delta, nu, qaz in self._calc_remaining_detector_angles(
                                        det_constraint_name, det_constraint, theta):
                if is_small(naz_qaz_angle):
                    naz_angles = [qaz,]
                else:
                    naz_angles = [qaz - naz_qaz_angle, qaz + naz_qaz_angle]
                for naz in naz_angles:
                    yield qaz, naz, delta, nu
        elif naz_constraint: # The 'detector' angle naz is given:
            det_constraint_name, det_constraint = naz_constraint.items()[0]
            naz_name, naz = det_constraint_name, det_constraint
            assert naz_name == 'naz'
            if is_small(naz_qaz_angle):
                qaz_angles = [naz,]
            else:
                qaz_angles = [naz - naz_qaz_angle, naz + naz_qaz_angle]
            for qaz in qaz_angles:
                for delta, nu, _ in self._calc_remaining_detector_angles(
                                        'qaz', qaz, theta):
                    yield qaz, naz, delta, nu

    def _calc_remaining_detector_angles(self, constraint_name,
                                        constraint_value, theta):
        """Return delta, nu and qaz given one detector angle
        """
        #                                                         (section 5.1)
        # Find qaz using various derivations of 17 and 18
        sin_2theta = sin(2 * theta)
        cos_2theta = cos(2 * theta)
        if is_small(sin_2theta):
            raise DiffcalcException(
                'No meaningful scattering vector (Q) can be found when '
                'theta is so small (%.4f).' % theta * TODEG)

        if constraint_name == 'delta':
            delta = constraint_value
            asin_qaz = asin(bound(sin(delta) / sin_2theta))              # (17 & 18)
            cos_delta = cos(delta)
            if is_small(cos_delta):
                #raise DiffcalcException(
                #    'The %s and %s circles are redundant when delta is constrained to %.0f degrees.'
                #    'Please change delta constraint or use 4-circle mode.' % (NUNAME, 'mu', delta * TODEG))
                print (('DEGENERATE: with delta=90, %s is degenerate: choosing '
                       '%s = 0 (allowed because %s is unconstrained)') %
                       (NUNAME, NUNAME, NUNAME))
                acos_nu = 1.
            else:
                acos_nu = acos(bound(cos_2theta / cos_delta))
            sgn_ref = sign(sin_2theta) * sign(cos_delta)
            if is_small(cos(asin_qaz)):
                qaz_angles = [sign(asin_qaz) * pi / 2.,]
            else:
                qaz_angles = [asin_qaz, pi - asin_qaz]
            if is_small(acos_nu):
                nu_angles = [0.,]
            else:
                nu_angles = [acos_nu, -acos_nu]
            for qaz, nu in product(qaz_angles, nu_angles):
                sgn_ratio = sign(sin(nu)) * sign(cos(qaz))
                if sgn_ref == sgn_ratio:
                    yield delta, nu, qaz

        elif constraint_name == NUNAME:
            nu = constraint_value
            cos_nu = cos(nu)
            if is_small(cos_nu):
                raise DiffcalcException(
                    'The %s circle constraint to %.0f degrees is redundant.'
                    'Please change this constraint or use 4-circle mode.' % (NUNAME, nu * TODEG))
            cos_delta = cos_2theta / cos(nu)
            cos_qaz = cos_delta * sin(nu) / sin_2theta
            acos_delta = acos(bound(cos_delta))
            acos_qaz = acos(bound(cos_qaz))
            sgn_ref = sign(sin_2theta)
            if is_small(acos_qaz):
                qaz_angles = [0.,]
            else:
                qaz_angles = [acos_qaz, -acos_qaz]
            if is_small(acos_delta):
                delta_angles = [0.,]
            else:
                delta_angles = [acos_delta, -acos_delta]
            for qaz, delta in product(qaz_angles, delta_angles):
                sgn_ratio = sign(sin(qaz)) * sign(sin(delta))
                if sgn_ref == sgn_ratio:
                    yield delta, nu, qaz

        elif constraint_name == 'qaz':
            qaz = constraint_value
            asin_delta = asin(sin(qaz) * sin_2theta)
            if is_small(cos(asin_delta)):
                delta_angles = [sign(asin_delta) * pi / 2.,]
            else:
                delta_angles = [asin_delta, pi - asin_delta]
            for delta in delta_angles:
                cos_delta = cos(delta)
                if is_small(cos_delta):
                    print (('DEGENERATE: with delta=90, %s is degenerate: choosing '
                           '%s = 0 (allowed because %s is unconstrained)') %
                           (NUNAME, NUNAME, NUNAME))
                    #raise DiffcalcException(
                    #    'The %s circle is redundant when delta is at %.0f degrees.'
                    #    'Please change detector constraint or use 4-circle mode.' % (NUNAME, delta * TODEG))
                    nu = 0.
                else:
                    sgn_delta = sign(cos_delta)
                    nu = atan2(sgn_delta * sin_2theta * cos(qaz), sgn_delta * cos_2theta)
                yield delta, nu, qaz
        else:
            raise DiffcalcException(
                constraint_name + ' is not an explicit detector angle '
                '(naz cannot be handled here)')


    def _calc_sample_angles_from_one_sample_constraint(
            self, h, k, l, wavelength, samp_constraints, h_phi, theta,
            ref_constraint_name, ref_constraint_value, alpha, qaz, naz, delta, nu):
        
        sample_constraint_name, sample_value = samp_constraints.items()[0]
        q_lab = matrix([[cos(theta) * sin(qaz)], 
                [-sin(theta)], 
                [cos(theta) * cos(qaz)]]) # (18)
        n_lab = matrix([[cos(alpha) * sin(naz)], 
                [-sin(alpha)], 
                [cos(alpha) * cos(naz)]]) # (20)
        mu_eta_chi_phi_tuples = list(self._calc_remaining_sample_angles(
            sample_constraint_name, sample_value, q_lab, n_lab, h_phi, 
            self._get_n_phi()))
        return mu_eta_chi_phi_tuples

    def _calc_sample_given_two_sample_and_reference(
            self, h, k, l, wavelength, samp_constraints, h_phi, theta,
            ref_constraint_name, ref_constraint_value, psi):
        
        for angles in self._calc_sample_angles_given_two_sample_and_reference(
                 samp_constraints, psi, theta, h_phi, self._get_n_phi()):
            qaz, psi, mu, eta, chi, phi = angles 
            values_in_deg = tuple(v * TODEG for v in angles)
            logger.info('Initial angles: xi=%.3f, psi=%.3f, mu=%.3f, '
                'eta=%.3f, chi=%.3f, phi=%.3f' % 
                values_in_deg) # Try to find a solution for each possible transformed xi

            logger.info("")
            msg = "---Trying psi=%.3f, qaz=%.3f" % (psi * TODEG, qaz * TODEG)
            logger.info(msg)
            
            for delta, nu, _ in self._calc_remaining_detector_angles('qaz', qaz, theta):
                logger.info("delta=%.3f, %s=%.3f", delta * TODEG, NUNAME, nu * TODEG)
                #for mu, eta, chi, phi in self._generate_sample_solutions(
                #    mu, eta, chi, phi, samp_constraints.keys(), delta, 
                #    nu, wavelength, (h, k, l), ref_constraint_name, 
                #    ref_constraint_value):
                yield mu, delta, nu, eta, chi, phi

    def _calc_remaining_sample_angles(self, constraint_name, constraint_value,
                                      q_lab, n_lab, q_phi, n_phi):
        """Return phi, chi, eta and mu, given one of these"""
        #                                                         (section 5.3)
        # TODO: Sould return a valid solution, rather than just one that can
        # be mapped to a correct solution by applying +-x and 180+-x mappings?


        N_lab = _calc_N(q_lab, n_lab)
        N_phi = _calc_N(q_phi, n_phi)
        Z = N_lab * N_phi.T

        if constraint_name == 'mu':                                      # (35)
            mu = constraint_value
            V = calcMU(mu).I * N_lab * N_phi.T
            acos_chi = acos(bound(V[2, 2]))
            if is_small(sin(acos_chi)):
                # chi ~= 0 or 180 and therefor phi || eta The solutions for phi
                # and eta here will be valid but will be chosen unpredictably.
                # Choose eta=0:
                #
                # tan(phi+eta)=v12/v11 from docs/extensions_to_yous_paper.wxm
                chi = acos_chi
                eta = 0.
                phi = atan2(-V[1, 0], V[1, 1])
                logger.debug(
                    'Eta and phi cannot be chosen uniquely with chi so close '
                    'to 0 or 180. Returning phi=%.3f and eta=%.3f', 
                    phi * TODEG, eta * TODEG)
                yield mu, eta, chi, phi
            else:
                for chi in [acos_chi, -acos_chi]:
                    sgn = sign(sin(chi))
                    phi = atan2(-sgn * V[2, 1], -sgn * V[2, 0])
                    eta = atan2(-sgn * V[1, 2],  sgn * V[0, 2])
                    yield mu, eta, chi, phi

        elif constraint_name == 'phi':                                     # (37)
            phi = constraint_value
            V = N_lab * N_phi.I * calcPHI(phi).T
            asin_eta = asin(bound(V[0, 1]))
            if is_small(cos(asin_eta)):
                raise DiffcalcException('Chi and mu cannot be chosen uniquely '
                                        'with eta so close to +/-90.')
            for eta in [asin_eta, pi - asin_eta]:
                sgn = sign(cos(eta))
                mu = atan2(sgn * V[2, 1], sgn * V[1, 1])
                chi = atan2(sgn * V[0, 2], sgn * V[0, 0])
                yield mu, eta, chi, phi

        elif constraint_name in ('eta', 'chi'):
            if constraint_name == 'eta':                                 # (39)
                eta = constraint_value
                cos_eta = cos(eta)
                if is_small(cos_eta):
                    #TODO: Not likely to happen in real world!?
                    raise DiffcalcException(
                        'Chi and mu cannot be chosen uniquely with eta '
                        'constrained so close to +-90.')
                asin_chi = asin(Z[0, 2] / cos_eta)
                all_eta = [eta,]
                all_chi = [asin_chi, pi - asin_chi]

            else:  # constraint_name == 'chi'                            # (40)
                chi = constraint_value
                sin_chi = sin(chi)
                if is_small(sin_chi):
                    raise DiffcalcException(
                        'Eta and phi cannot be chosen uniquely with chi '
                        'constrained so close to 0. (Please contact developer '
                        'if this case is useful for you)')
                acos_eta = acos(Z[0, 2] / sin_chi)
                all_eta = [acos_eta, -acos_eta]
                all_chi = [chi,]

            for chi, eta in product(all_chi, all_eta):
                top_for_mu = Z[2, 2] * sin(eta) * sin(chi) + Z[1, 2] * cos(chi)
                bot_for_mu = -Z[2, 2] * cos(chi) + Z[1, 2] * sin(eta) * sin(chi)
                if is_small(top_for_mu) and is_small(bot_for_mu):
                    # chi == +-90, eta == 0/180 and therefore phi || mu cos(chi) ==
                    # 0 and sin(eta) == 0 Experience shows that even though e.g.
                    # the z[2, 2] and z[1, 2] values used to calculate mu may be
                    # basically 0 (1e-34) their ratio in every case tested so far
                    # still remains valid and using them will result in a phi
                    # solution that is continuous with neighbouring positions.
                    #
                    # We cannot test phi minus mu here unfortunately as the final
                    # phi and mu solutions have not yet been chosen (they may be
                    # +-x or 180+-x). Otherwise we could choose a sensible solution
                    # here if the one found was incorrect.

                    # tan(phi+eta)=v12/v11 from extensions_to_yous_paper.wxm
                    phi_minus_mu = -atan2(Z[2, 0], Z[1, 1])
                    logger.debug(
                        'Mu and phi cannot be chosen uniquely with chi so close '
                        'to +/-90 and eta so close 0 or 180.\n After the final '
                        'solution has been chose phi-mu should equal: %.3f',
                        phi_minus_mu * TODEG)
                mu = atan2(-top_for_mu, -bot_for_mu)                         # (41)

                top_for_phi = Z[0, 1] * cos(eta) * cos(chi) - Z[0, 0] * sin(eta)
                bot_for_phi = Z[0, 1] * sin(eta) + Z[0, 0] * cos(eta) * cos(chi)
                phi = atan2(top_for_phi, bot_for_phi)                        # (42)
    #            if is_small(bot_for_phi) and is_small(top_for_phi):
    #                raise DiffcalcException(
    #                    'phi=%.3f cannot be known with confidence as top and '
    #                    'bottom are both close to zero. chi=%.3f, eta=%.3f'
    #                    % (mu * TODEG, chi * TODEG, eta * TODEG))
                yield mu, eta, chi, phi

        else:
            raise DiffcalcException('Given angle must be one of phi, chi, eta or mu')

    def _calc_angles_given_three_sample_constraints(
            self, h, k, l, wavelength, return_all_solutions, samp_constraints,
            h_phi, theta):
        
        if not 'mu' in samp_constraints:
            eta_ = self.constraints.sample['eta']
            chi_ = self.constraints.sample['chi']
            phi_ = self.constraints.sample['phi']
            two_mu_qaz_pairs = _mu_and_qaz_from_eta_chi_phi(eta_, chi_, phi_, theta, h_phi)
        else:
            raise DiffcalcException(
                'No code yet to handle this combination of 3 sample constraints!')
    # TODO: Code duplicated above
        all_solutions = []
        for mu_, qaz in two_mu_qaz_pairs:
            logger.debug("--- Trying mu_:%.f qaz_%.f", mu_ * TODEG, qaz * TODEG)
            for delta, nu, _ in self._calc_remaining_detector_angles('qaz', qaz, theta):
                logger.info("delta=%.3f, %s=%.3f", delta * TODEG, NUNAME, nu * TODEG)
                all_solutions.append((mu_, delta, nu, eta_, chi_, phi_))
        
        return all_solutions

    def _calc_sample_angles_given_two_sample_and_reference(
            self, samp_constraints, psi, theta, q_phi, n_phi):
        """Available combinations:
        chi, phi, reference
        mu, eta, reference,
        chi=90, mu=0, reference
        """

        N_phi = _calc_N(q_phi, n_phi)
        THETA = z_rotation(-theta)
        PSI = x_rotation(psi)

        if 'chi' in samp_constraints and 'phi' in samp_constraints:

            chi = samp_constraints['chi']
            phi = samp_constraints['phi']

            CHI = calcCHI(chi)
            PHI = calcPHI(phi)
            V = CHI * PHI * N_phi * PSI.T * THETA.T                     # (46)

            #atan2_xi = atan2(-V[2, 0], V[2, 2])
            #atan2_eta = atan2(-V[0, 1], V[1, 1])
            #atan2_mu = atan2(-V[2, 1], sqrt(V[2, 2] ** 2 + V[2, 0] ** 2))
            asin_mu = asin(-V[2, 1])
            for mu in [asin_mu, pi - asin_mu]:
                sgn_cosmu = sign(cos(mu))
                #xi = atan2(-sgn_cosmu * V[2, 0], sgn_cosmu * V[2, 2])
                qaz = atan2(sgn_cosmu * V[2, 2], sgn_cosmu * V[2, 0], )
                eta = atan2(-sgn_cosmu * V[0, 1], sgn_cosmu * V[1, 1])
                yield qaz, psi, mu, eta, chi, phi

        elif 'mu' in samp_constraints and 'eta' in samp_constraints:

            mu = samp_constraints['mu']
            eta = samp_constraints['eta']

            V = N_phi * PSI.T * THETA.T                                  # (49)

            bot = -V[2, 1] / sqrt(sin(eta) ** 2 * cos(mu) ** 2 + sin(mu) ** 2)
            if is_small(cos(mu) * sin(eta)):
                eps = atan2(sin(eta) * cos(mu), sin(mu))
                chi_vals = [eps + acos(bot), eps - acos(bot)]
            else:
                eps = atan2(sin(mu), sin(eta) * cos(mu))
                chi_vals = [asin(bot) - eps, pi - asin(bot) - eps]       # (52)

            ## Choose final chi solution here to obtain compatable xi and mu
            ## TODO: This temporary solution works only for one case used on i07
            ##       Return a list of possible solutions?
            #if is_small(eta) and is_small(mu + pi / 2):
            #    for chi in _generate_transformed_values(chi_orig):
            #        if  pi / 2 <= chi < pi:
            #            break
            #else:
            #    chi = chi_orig

            for chi in chi_vals:
                a = sin(chi) * cos(eta)
                b = sin(chi) * sin(eta) * sin(mu) - cos(chi) * cos(mu)
                #atan2_xi = atan2(V[2, 2] * a + V[2, 0] * b,
                #           V[2, 0] * a - V[2, 2] * b)                        # (54)
                qaz = atan2(V[2, 0] * a - V[2, 2] * b,
                           -V[2, 2] * a - V[2, 0] * b)                        # (54)
    
                a = sin(chi) * sin(mu) - cos(mu) * cos(chi) * sin(eta)
                b = cos(mu) * cos(eta)
                phi = atan2(V[1, 1] * a - V[0, 1] * b,
                            V[0, 1] * a + V[1, 1] * b)                       # (55)
    #            if is_small(mu+pi/2) and is_small(eta) and False:
    #                phi_general = phi
    #                # solved in extensions_to_yous_paper.wxm
    #                phi = atan2(V[1, 1], V[0, 1])
    #                logger.info("phi = %.3f or %.3f (std)",
    #                            phi*TODEG, phi_general*TODEG )
    
                yield qaz, psi, mu, eta, chi, phi

        elif 'chi' in samp_constraints and 'mu' in samp_constraints:

            chi = samp_constraints['chi']
            mu = samp_constraints['mu']

            V = N_phi * PSI.T * THETA.T                                  # (49)

            asin_eta = asin(bound((-V[2, 1] - cos(chi) * sin(mu)) / (sin(chi) * cos(mu))))

            for eta in [asin_eta, pi - asin_eta]:
                a = sin(chi) * cos(eta)
                b = sin(chi) * sin(eta) * sin(mu) - cos(chi) * cos(mu)
                #atan2_xi = atan2(V[2, 2] * a + V[2, 0] * b,
                #           V[2, 0] * a - V[2, 2] * b)                        # (54)
                qaz = atan2(V[2, 0] * a - V[2, 2] * b,
                           -V[2, 2] * a - V[2, 0] * b)                        # (54)
    
                a = sin(chi) * sin(mu) - cos(mu) * cos(chi) * sin(eta)
                b = cos(mu) * cos(eta)
                phi = atan2(V[1, 1] * a - V[0, 1] * b,
                            V[0, 1] * a + V[1, 1] * b)                       # (55)
                yield qaz, psi, mu, eta, chi, phi

        else:
            raise DiffcalcException(
                'No code yet to handle this combination of 2 sample '
                'constraints and one reference!:' + str(samp_constraints))

    def _calc_sample_angles_given_two_sample_and_detector(
            self, samp_constraints, qaz, theta, q_phi, n_phi):
        """Available combinations:
        chi, phi, detector
        mu, eta, detector
        """

        N_phi = _calc_N(q_phi, n_phi)

        if 'mu' in samp_constraints and 'eta' in samp_constraints:

            mu = samp_constraints['mu']
            eta = samp_constraints['eta']
            
            F = y_rotation(qaz - pi/2.)
            THETA = z_rotation(-theta)
            V = calcETA(eta).T * calcMU(mu).T * F * THETA                       # (56)

            bot = -V[1, 0] / sqrt(N_phi[0, 0]**2 + N_phi[1, 0]**2)
            eps = atan2(N_phi[1, 0], N_phi[0, 0])
            for phi in [asin(bot) + eps, pi - asin(bot) + eps]:                 # (59)
                a = N_phi[0, 0] * cos(phi) + N_phi[1, 0] * sin(phi)
                chi = atan2(N_phi[2, 0] * V[0, 0] - a * V[2, 0],
                            N_phi[2, 0] * V[2, 0] + a * V[0, 0])                # (60)
                yield mu, eta, chi, phi

        elif 'chi' in samp_constraints and 'phi' in samp_constraints:

            chi = samp_constraints['chi']
            phi = samp_constraints['phi']

            CHI = calcCHI(chi)
            PHI = calcPHI(phi)
            V = CHI * PHI * N_phi                     # (62)

            bot = V[2, 0] / sqrt(cos(qaz) ** 2 * cos(theta) ** 2 + sin(theta) ** 2)
            eps = atan2(-cos(qaz) * cos(theta), sin(theta))
            for mu in [asin(bot) + eps, pi - asin(bot) + eps]:
                a = cos(theta) * sin(qaz)
                b = -cos(theta) * sin(mu) * cos(qaz) + cos(mu) * sin(theta)
                eta = atan2(V[1, 0] * a + V[0, 0] * b, V[0, 0] * a - V[1, 0]* b)
                
                #a = -cos(mu) * cos(qaz) * sin(theta) + sin(mu) * cos(theta)
                #b = cos(mu) * sin(qaz)
                #psi = atan2(-V[2, 2] * a - V[2, 1] * b, V[2, 1] * a - V[2, 2] * b)
                yield mu, eta, chi, phi

        elif 'mu' in samp_constraints and 'phi' in samp_constraints:

            mu = samp_constraints['mu']
            phi = samp_constraints['phi']

            F = y_rotation(qaz - pi/2.)
            THETA = z_rotation(-theta)
            V = calcMU(mu).T * F * THETA
            E = calcPHI(phi) * N_phi
            
            bot = -V[2, 0] / sqrt(E[0, 0]**2 + E[2, 0]**2)
            eps = atan2(E[2, 0], E[0, 0])
            for chi in [asin(bot) + eps, pi - asin(bot) + eps]:
                a = E[0, 0] * cos(chi) + E[2, 0] * sin(chi)
                eta = atan2(V[0, 0] * E[1, 0] - V[1, 0] * a, V[0, 0] * a + V[1, 0] * E[1, 0])
                yield mu, eta, chi, phi
        else:
            raise DiffcalcException(
                'No code yet to handle this combination of 2 sample '
                'constraints and one detector!:' + str(samp_constraints))

    def _filter_angle_limits(self, possible_solutions, angle_names,
                                filter_out_of_limits=True):
        res = []
        for possible_solution in possible_solutions:
            sol = []
            for name, value in zip(angle_names, possible_solution):
                if name in self._hardware.get_axes_names():
                    sol.append(self._hardware.cut_angle(name, value * TODEG) * TORAD)
                else:
                    sol.append(value)
            if not filter_out_of_limits:
                res.append(tuple(sol))
            else:
                is_in_limits = [self._hardware.is_axis_value_within_limits(name, value * TODEG) for name, value in zip(angle_names, sol)
                                if name in self._hardware.get_axes_names()]
                if not False in is_in_limits:
                    res.append(tuple(sol))
        return res

def _mu_and_qaz_from_eta_chi_phi(eta, chi, phi, theta, h_phi):
    
    h_phi_norm = normalised(h_phi)                                    # (68,69) 
    h1, h2, h3 = h_phi_norm[0, 0], h_phi_norm[1, 0], h_phi_norm[2, 0]
    a = sin(chi) * h2 * sin(phi) + sin(chi) * h1 * cos(phi) - cos(chi) * h3
    b = (- cos(chi) * sin(eta) * h2 * sin(phi)
         - cos(eta) * h1 * sin(phi) + cos(eta) * h2 * cos(phi)
         - cos(chi) * sin(eta) * h1 * cos(phi)
         - sin(chi) * sin(eta) * h3)
    c = -sin(theta)
    sin_bit = bound(c / sqrt(a * a + b * b))
    mu1 = asin(sin_bit) - atan2(b, a)
    mu2 = pi - asin(sin_bit) - atan2(b, a)

    mu1 = cut_at_minus_pi(mu1)
    mu2 = cut_at_minus_pi(mu2)
    
    # TODO: This special case should be *removed* when the general case has shown
    # to encompass it. It exists as fallback for a particular i16 experiment in
    # May 2013 --RobW.
#     if eta == chi == 0:
#         logger.debug("Testing against simplified equations for eta == chi == 0")
#         a = - h3
#         b = - h1 * sin(phi) + h2 * cos(phi)
#         sin_bit = bound(c / sqrt(a * a + b * b))
#         mu_simplified = pi - asin(sin_bit) - atan2(b, a)
#         mu_simplified = cut_at_minus_pi(mu_simplified)
#         if not ne(mu_simplified, mu):
#             raise AssertionError("mu_simplified != mu , %f!=%f" % (mu_simplified, mu))
        
    
    [MU, _, _, ETA, CHI, PHI] = create_you_matrices(mu1, None, None, eta, chi, phi)
    h_lab = MU * ETA * CHI * PHI * h_phi                                 # (11)
    qaz1 = atan2(h_lab[0, 0] , h_lab[2, 0])

    [MU, _, _, ETA, CHI, PHI] = create_you_matrices(mu2, None, None, eta, chi, phi)
    h_lab = MU * ETA * CHI * PHI * h_phi                                 # (11)
    qaz2 = atan2(h_lab[0, 0] , h_lab[2, 0])

    return (mu1, qaz1) , (mu2, qaz2)
