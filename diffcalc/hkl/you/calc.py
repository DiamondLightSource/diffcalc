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

from math import pi, sin, cos, tan, acos, atan2, asin, sqrt, atan

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm

from diffcalc.log import logging
from diffcalc.hkl.calcbase import HklCalculatorBase
from diffcalc.hkl.you.geometry import create_you_matrices, calcMU, calcPHI, \
    calcCHI
from diffcalc.hkl.you.geometry import YouPosition
from diffcalc.util import DiffcalcException, bound, angle_between_vectors
from diffcalc.util import cross3, z_rotation, x_rotation
from diffcalc.ub.calc import PaperSpecificUbCalcStrategy

from diffcalc.hkl.you.constraints import NUNAME
logger = logging.getLogger("diffcalc.hkl.you.calc")
I = matrix('1 0 0; 0 1 0; 0 0 1')
y = matrix('0; 1; 0')

SMALL = 1e-8
TORAD = pi / 180
TODEG = 180 / pi

PRINT_DEGENERATE = False


def is_small(x):
    return abs(x) < SMALL


def ne(a, b):
    return is_small(a - b)


def sequence_ne(a_seq, b_seq):
    for a, b in zip(a_seq, b_seq):
        if not ne(a, b):
            return False
    return True


def sign(x):
    return 1 if x > 0 else -1


def normalised(vector):
    return vector * (1 / norm(vector))


def cut_at_minus_pi(value):
    if value < (-pi - SMALL):
        return value + 2 * pi
    if value >= pi + SMALL:
        return value - 2 * pi
    return value


def merge_nearly_equal_pairs(delta_nu_pairs):
    
    def pair_nearly_in_pair_list(pair, pair_list):
        for a, b in pair_list:
            if ne(pair[0], a) and ne(pair[1], b):
                return True
        return False
    
    merged = []
    for pair in delta_nu_pairs:
        if not pair_nearly_in_pair_list(pair, merged):
            merged.append(pair)
    return merged


def _calc_N(Q, n):
    """Return N as described by Equation 31"""
    Q = normalised(Q)
    n = normalised(n)
    if is_small(angle_between_vectors(Q, n)):
        raise ValueError('Q and n are parallel and cannot be used to create '
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

    if nu_constrained_to_0 and mu_constrained_to_0:
        # constrained to vertical 4-circle like mode
        if is_small(pos.chi):  # phi || eta
            desired_eta = pos.delta / 2.
            eta_diff = desired_eta - pos.eta
            pos.eta += eta_diff
            pos.phi -= eta_diff
            if PRINT_DEGENERATE:
                print ('DEGENERATE: with chi=0, phi and eta are colinear:'
                       'choosing eta = delta/2 by adding % 7.3f to eta and '
                       'removing it from phi. (mu=%s=0 only)' % (eta_diff * TODEG, NUNAME))
                print '            original:', original

    elif delta_constrained_to_0 and eta_constrained_to_0:
        # constrained to horizontal 4-circle like mode
        if is_small(pos.chi - pi / 2):  # phi || mu
            desired_mu = pos.nu / 2.
            mu_diff = desired_mu - pos.mu
            pos.mu += mu_diff
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
    qaz = atan2(tan(delta), sin(nu))
    return theta, qaz


def _filter_detector_solutions_by_theta_and_qaz(possible_delta_nu_pairs,
                                                required_theta, required_qaz):
    delta_nu_pairs = []
    for delta, nu in possible_delta_nu_pairs:
        theta, qaz = _theta_and_qaz_from_detector_angles(delta, nu)
        if ne(theta, required_theta) and ne(qaz, required_qaz):
            delta_nu_pairs.append((delta, nu))
    return delta_nu_pairs


def _generate_transformed_values(value, constrained=False):
    if constrained:
        yield value
    elif is_small(value):
        yield 0.
        yield pi
    elif is_small(value - pi / 2) or is_small(value + pi / 2):
        yield pi / 2
        yield -pi / 2
    else:
        yield value
        yield -value
        yield pi + value
        yield pi - value


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
        return self._ubcalc.reference.n_phi
    
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

        sin_tau = sin(tau)
        cos_theta = cos(theta)
        if sin_tau == 0:
            psi = float('Nan')
            print ('WARNING: Diffcalc could not calculate a unique azimuth '
                   '(psi) as the scattering vector (Q) and the reference '
                   'vector (n) are parallel')
        elif cos_theta == 0:
            psi = float('Nan')
            print ('WARNING: Diffcalc could not calculate a unique azimuth '
                   '(psi) because the scattering vector (Q) and xray beam are '
                   " are parallel and don't form a unique reference plane")
        else:
            cos_psi = ((cos(tau) * sin(theta) - sin(alpha)) /
                       (sin_tau * cos_theta))
            psi = acos(bound(cos_psi))                                   # (28)

        return {'theta': theta, 'qaz': qaz, 'alpha': alpha,
                'naz': naz, 'tau': tau, 'psi': psi, 'beta': beta}


    def hklToAngles(self, h, k, l, wavelength):
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

        pos_virtual_angles_pairs = self._hklToAngles(h, k, l, wavelength)  # in rad
        assert len(pos_virtual_angles_pairs) == 1
        pos, virtual_angles = pos_virtual_angles_pairs[0]
            
        # to degrees:
        pos.changeToDegrees()
        for key, val in virtual_angles.items():
            if val is not None:
                virtual_angles[key] = val * TODEG

        self._verify_pos_map_to_hkl(h, k, l, wavelength, pos)

        return pos, virtual_angles

    def hkl_to_all_angles(self, h, k, l, wavelength):
        pos_virtual_angles_pairs = self._hklToAngles(h, k, l, wavelength,
                                                     return_all_solutions=True)  # in rad
        assert pos_virtual_angles_pairs
        
        pos_virtual_angles_pairs_in_degrees = []
        
        for pos, virtual_angles in pos_virtual_angles_pairs:
            pos.changeToDegrees()
            for key, val in virtual_angles.items():
                if val is not None:
                    virtual_angles[key] = val * TODEG
    
            self._verify_pos_map_to_hkl(h, k, l, wavelength, pos)
            pos_virtual_angles_pairs_in_degrees.append((pos, virtual_angles))
        return pos_virtual_angles_pairs_in_degrees
        

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
            psi, alpha, _ = self._calc_remaining_reference_angles(
                ref_constraint_name, ref_constraint_value, theta, tau)

        ### Detector constraint column ###

        if det_constraint or naz_constraint:
            qaz, naz, delta, nu = self._calc_det_angles_given_det_or_naz_constraint(
                                  det_constraint, naz_constraint, theta, tau, alpha)
        
        ### Sample constraint column ###

        if len(samp_constraints) == 1:
            # a detector and reference constraint will have been given
            mu, eta, chi, phi = self._calc_sample_angles_from_one_sample_constraint(
                h, k, l, wavelength, samp_constraints, h_phi, theta,
                ref_constraint_name, ref_constraint_value, alpha, qaz, naz,
                delta, nu)
            solution_tuples = [(mu, delta, nu, eta, chi, phi)]

        elif len(samp_constraints) == 2:
            assert ref_constraint, ('No code yet to handle 2 sample '
                                    'without a reference constraint!')
            angles = self._calc_sample_given_two_sample_and_reference(
                h, k, l, wavelength, samp_constraints, h_phi, theta,
                ref_constraint_name, ref_constraint_value, psi)
            solution_tuples = [angles]

        elif len(samp_constraints) == 3:
            solution_tuples = self._calc_angles_given_three_sample_constraints(
                h, k, l, wavelength, return_all_solutions, samp_constraints,
                 h_phi, theta)
            
        position_pseudo_angles_pairs = []
        for mu, delta, nu, eta, chi, phi in solution_tuples:
            pair = self._create_position_pseudo_angles_pair(
                wavelength, mu, delta, nu, eta, chi, phi)
            position_pseudo_angles_pairs.append(pair)

        return position_pseudo_angles_pairs



    def _create_position_pseudo_angles_pair(self, wavelength, mu, delta, nu, eta, chi, phi):
        # Create position
        position = YouPosition(mu, delta, nu, eta, chi, phi)
        position = _tidy_degenerate_solutions(position, self.constraints)
        if position.phi <= -pi + SMALL:
            position.phi += 2 * pi
        # pseudo angles calculated along the way were for the initial solution
        # and may be invalid for the chosen solution TODO: anglesToHkl need no
        # longer check the pseudo_angles as they will be generated with the
        # same function and it will prove nothing
        pseudo_angles = self._anglesToVirtualAngles(position, wavelength)
        return position, pseudo_angles


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

    def _calc_remaining_reference_angles(self, name, value, theta, tau):
        """Return psi, alpha and beta given one of a_eq_b, alpha, beta or psi
        """
        if sin(tau) == 0:
            raise DiffcalcException(
                'The scattering vector (Q) and the reference vector (n) are\n'
                'parallel. The constraint %s could not be used to determine a\n'
                'unique azimuthal rotation about the Q vector.' % name)
        if cos(theta) == 0:
            raise DiffcalcException(
                'The constraint %s could not be used to determine a unique '
                'azimuth (psi) as the scattering vector (Q) and xray beam are '
                "are parallel and don't form a unique'reference plane" % name)

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

        if name != 'psi':
            cos_psi = ((cos(tau) * sin(theta) - sin(alpha)) /            # (28)
                       (sin(tau) * cos(theta)))
            if abs(cos_psi) > (1 + SMALL):
                hint = "\nAlpha may be too low?" if name == 'alpha' else "";
                raise DiffcalcException(UNREACHABLE_MSG % (name, value * TODEG) + hint)
            # TODO: If set, alpha is probably too low

            psi = acos(bound(cos_psi))
        return psi, alpha, beta

    def _calc_det_angles_given_det_or_naz_constraint(
            self, det_constraint, naz_constraint, theta, tau, alpha):
        
        assert det_constraint or naz_constraint
        
        if det_constraint:
            # One of the detector angles is given                 (Section 5.1)
            det_constraint_name, det_constraint = det_constraint.items()[0]
            delta, nu, qaz = self._calc_remaining_detector_angles(
                             det_constraint_name, det_constraint, theta)
            naz_qaz_angle = _calc_angle_between_naz_and_qaz(theta, alpha, tau)
            naz = qaz - naz_qaz_angle
            
        elif naz_constraint: # The 'detector' angle naz is given:
            det_constraint_name, det_constraint = naz_constraint.items()[0]
            naz_name, naz = det_constraint_name, det_constraint
            assert naz_name == 'naz'
            naz_qaz_angle = _calc_angle_between_naz_and_qaz(theta, alpha, tau)
            qaz = naz - naz_qaz_angle
            nu = atan2(sin(2 * theta) * cos(qaz), cos(2 * theta))
            delta = atan2(sin(qaz) * sin(nu), cos(qaz))
            
        delta_nu_pairs = self._generate_detector_solutions(
                         delta, nu, qaz, theta, det_constraint_name)
        if not delta_nu_pairs:
            raise DiffcalcException('No detector solutions were found,'
                'please unconstrain detector limits')
        delta, nu = self._choose_detector_solution(delta_nu_pairs)
        
        return qaz, naz, delta, nu

    def _calc_remaining_detector_angles(self, constraint_name,
                                        constraint_value, theta):
        """Return delta, nu and qaz given one detector angle
        """
        #                                                         (section 5.1)
        # Find qaz using various derivations of 17 and 18
        if constraint_name == 'delta':
            delta = constraint_value
            sin_2theta = sin(2 * theta)
            if is_small(sin_2theta):
                raise DiffcalcException(
                    'No meaningful scattering vector (Q) can be found when '
                    'theta is so small (%.4f).' % theta * TODEG)
            qaz = asin(bound(sin(delta) / sin_2theta))              # (17 & 18)

        elif constraint_name == NUNAME:
            nu = constraint_value
#            cos_delta = cos(2*theta) / cos(nu)#<--fails when nu = 90
#            delta = acos(bound(cos_delta))
#            tan
            sin_2theta = sin(2 * theta)
            if is_small(sin_2theta):
                raise DiffcalcException(
                    'No meaningful scattering vector (Q) can be found when '
                    'theta is so small (%.4f).' % theta * TODEG)
            cos_qaz = tan(nu) / tan(2 * theta)
            if abs(cos_qaz) > 1 + SMALL:
                raise DiffcalcException(
                    'The specified %s=%.4f is greater than the 2theta (%.4f)'
                    % (NUNAME, nu, theta))
            qaz = acos(bound(cos_qaz))

        elif constraint_name == 'qaz':
            qaz = constraint_value

        else:
            raise ValueError(
                constraint_name + ' is not an explicit detector angle '
                '(naz cannot be handled here)')

        if constraint_name != NUNAME:
            nu = atan2(sin(2 * theta) * cos(qaz), cos(2 * theta))

        if constraint_name != 'delta':
            cos_qaz = cos(qaz)
            if not is_small(cos_qaz):  # TODO: switch methods at 45 deg?
                delta = atan2(sin(qaz) * sin(nu), cos_qaz)
            else:
                # qaz is close to 90 (a common place for it)
                delta = sign(qaz) * acos(bound(cos(2 * theta) / cos(nu)))

        return delta, nu, qaz

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
        phi, chi, eta, mu = self._calc_remaining_sample_angles(
            sample_constraint_name, sample_value, q_lab, n_lab, h_phi, 
            self._get_n_phi())
        mu_eta_chi_phi_tuples = self._generate_sample_solutions(
            mu, eta, chi, phi, (sample_constraint_name, ), 
            delta, nu, wavelength, (h, k, l), 
            ref_constraint_name, ref_constraint_value)
        if not mu_eta_chi_phi_tuples:
            raise DiffcalcException('No sample solutions were found,'
                'please un-constrain sample limits')
        mu, eta, chi, phi = self._choose_sample_solution(mu_eta_chi_phi_tuples)
        return mu, eta, chi, phi

    def _calc_sample_given_two_sample_and_reference(
            self, h, k, l, wavelength, samp_constraints, h_phi, theta,
            ref_constraint_name, ref_constraint_value, psi):
        
        angles = self._calc_sample_angles_given_two_sample_and_reference(
                 samp_constraints, psi, theta, h_phi, self._get_n_phi())
        xi_initial, psi, mu, eta, chi, phi = angles
        values_in_deg = tuple(v * TODEG for v in angles)
        logger.info('Initial angles: xi=%.3f, psi=%.3f, mu=%.3f, '
            'eta=%.3f, chi=%.3f, phi=%.3f' % 
            values_in_deg) # Try to find a solution for each possible transformed xi
        solution_found = False
        for xi in _generate_transformed_values(xi_initial, False):
            qaz = xi + pi / 2
            if qaz > 2 * pi:
                qaz -= 2 * pi
            logger.info("---Trying qaz=%.3f (from xi=%.3f)", qaz * TODEG, xi * TODEG)
            delta, nu, qaz = self._calc_remaining_detector_angles(
                'qaz', qaz, theta)
            delta_nu_pairs = self._generate_detector_solutions(
                delta, nu, qaz, theta, 'qaz')
            if not delta_nu_pairs:
                continue
            delta, nu = self._choose_detector_solution(delta_nu_pairs)
            logger.info("delta=%.3f, %s=%.3f", delta * TODEG, NUNAME, nu * TODEG)
            mu_eta_chi_phi_tuples = self._generate_sample_solutions(
                mu, eta, chi, phi, samp_constraints.keys(), delta, 
                nu, wavelength, (h, k, l), ref_constraint_name, 
                ref_constraint_value)
            if not mu_eta_chi_phi_tuples:
                continue
            mu, eta, chi, phi = self._choose_sample_solution(mu_eta_chi_phi_tuples)
            solution_found = True
            break
        if not solution_found:
            raise Exception('No solutions were found, please '
                'unconstrain detector or sample limits')
        return mu, delta, nu, eta, chi, phi

    def _calc_remaining_sample_angles(self, constraint_name, constraint_value,
                                      q_lab, n_lab, q_phi, n_phi):
        """Return phi, chi, eta and mu, given one of these"""
        #                                                         (section 5.3)
        # TODO: Sould return a valid solution, rather than just one that can
        # be mapped to a correct solution by applying +-x and 180+-x mappings?

        N_lab = _calc_N(q_lab, n_lab)
        N_phi = _calc_N(q_phi, n_phi)

        if constraint_name == 'mu':                                      # (35)
            mu = constraint_value
            V = calcMU(mu).I * N_lab * N_phi.T
            phi = atan2(V[2, 1], V[2, 0])
            eta = atan2(-V[1, 2], V[0, 2])
            chi = atan2(sqrt(V[2, 0] ** 2 + V[2, 1] ** 2), V[2, 2])
            if is_small(sin(chi)):
                # chi ~= 0 or 180 and therefor phi || eta The solutions for phi
                # and eta here will be valid but will be chosen unpredictably.
                # Choose eta=0:
                phi_orig, eta_orig = phi, eta
                # tan(phi+eta)=v12/v11 from docs/extensions_to_yous_paper.wxm
                eta = 0
                phi = atan2(V[0, 1], V[0, 0])
                logger.debug(
                    'Eta and phi cannot be chosen uniquely with chi so close '
                    'to 0 or 180. Ignoring solution phi=%.3f and eta=%.3f, and'
                    ' returning phi=%.3f and eta=%.3f', phi_orig * TODEG,
                    eta_orig * TODEG, phi * TODEG, eta * TODEG)
            return phi, chi, eta, mu

        if constraint_name == 'phi':                                     # (37)
            phi = constraint_value
            V = N_lab * N_phi.I * calcPHI(phi).T
            eta = atan2(V[0, 1], sqrt(V[1, 1] ** 2 + V[2, 1] ** 2))
            mu = atan2(V[2, 1], V[1, 1])
            chi = atan2(V[0, 2], V[0, 0])
            if is_small(cos(eta)):
                raise ValueError(
                    'Chi and mu cannot be chosen uniquely with eta so close '
                    'to +-90.')
            return phi, chi, eta, mu

        elif constraint_name in ('eta', 'chi'):
            V = N_lab * N_phi.T
            if constraint_name == 'eta':                                 # (39)
                eta = constraint_value
                cos_eta = cos(eta)
                if is_small(cos_eta):
                    #TODO: Not likely to happen in real world!?
                    raise ValueError(
                        'Chi and mu cannot be chosen uniquely with eta '
                        'constrained so close to +-90.')
                chi = asin(V[0, 2] / cos_eta)

            else:  # constraint_name == 'chi'                            # (40)
                chi = constraint_value
                sin_chi = sin(chi)
                if is_small(sin_chi):
                    raise ValueError(
                        'Eta and phi cannot be chosen uniquely with chi '
                        'constrained so close to 0. (Please contact developer '
                        'if this case is useful for you)')
                eta = acos(V[0, 2] / sin_chi)

            top_for_mu = V[2, 2] * sin(eta) * sin(chi) + V[1, 2] * cos(chi)
            bot_for_mu = -V[2, 2] * cos(chi) + V[1, 2] * sin(eta) * sin(chi)
            mu = atan2(-top_for_mu, -bot_for_mu)                         # (41)
            # (minus signs added from paper to pass (pieces) tests)
            if is_small(top_for_mu) and is_small(bot_for_mu):
                # chi == +-90, eta == 0/180 and therefor phi || mu cos(chi) ==
                # 0 and sin(eta) == 0 Experience shows that even though e.g.
                # the V[2, 2] and V[1, 2] values used to calculate mu may be
                # basically 0 (1e-34) their ratio in every case tested so far
                # still remains valid and using them will result in a phi
                # solution that is continous with neighbouring positions.
                #
                # We cannot test phi minus mu here unfortunetely as the final
                # phi and mu solutions have not yet been chosen (they may be
                # +-x or 180+-x). Otherwise we could choose a sensible solution
                # here if the one found was incorrect.

                # tan(phi+eta)=v12/v11 from extensions_to_yous_paper.wxm
                phi_minus_mu = -atan2(V[2, 0], V[1, 1])
                logger.debug(
                    'Mu and phi cannot be chosen uniquely with chi so close '
                    'to +-90 and eta so close 0 or 180.\n After the final '
                    'solution has been chose phi-mu should equal: %.3f',
                    phi_minus_mu * TODEG)

            top_for_phi = V[0, 1] * cos(eta) * cos(chi) - V[0, 0] * sin(eta)
            bot_for_phi = V[0, 1] * sin(eta) + V[0, 0] * cos(eta) * cos(chi)
            phi = atan2(top_for_phi, bot_for_phi)                        # (42)
#            if is_small(bot_for_phi) and is_small(top_for_phi):
#                raise ValueError(
#                    'phi=%.3f cannot be known with confidence as top and '
#                    'bottom are both close to zero. chi=%.3f, eta=%.3f'
#                    % (mu * TODEG, chi * TODEG, eta * TODEG))
            return phi, chi, eta, mu

        raise ValueError('Given angle must be one of phi, chi, eta or mu')

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
        working_delta_nu_pairs = []
        filter_out_of_limits = not return_all_solutions
        two_mu_qaz_pairs = merge_nearly_equal_pairs(two_mu_qaz_pairs)
        for mu_, qaz in two_mu_qaz_pairs:
            logger.debug("--- Trying mu_:%.f qaz_%.f", mu_ * TODEG, qaz * TODEG)
            delta_, nu_, _ = self._calc_remaining_detector_angles('qaz', qaz, theta)
            delta_nu_pairs = self._generate_detector_solutions(
                delta_, nu_, qaz, theta, 'qaz', filter_out_of_limits)
            for delta, nu in delta_nu_pairs:
                logger.info("delta=%.3f, %s=%.3f", delta * TODEG, NUNAME, nu * TODEG)
    #                delta, nu = self._choose_detector_solution(delta_nu_pairs)
                mu_eta_chi_phi_tuples = self._generate_sample_solutions(
                    mu_, eta_, chi_, phi_, samp_constraints.keys(), delta, 
                    nu, wavelength, (h, k, l), None, None, filter_out_of_limits)
                if mu_eta_chi_phi_tuples:
                    working_delta_nu_pairs.append((delta, nu))
                for mu, eta, chi, phi in mu_eta_chi_phi_tuples:
                    all_solutions.append((mu, delta, nu, eta, chi, phi))
        
        working_delta_nu_pairs = merge_nearly_equal_pairs(
            working_delta_nu_pairs)
        if return_all_solutions:
            return all_solutions
        
        elif not working_delta_nu_pairs:
            raise Exception('No solutions were found, please '
                'unconstrain detector or sample limits')
        elif len(working_delta_nu_pairs) > 1:
            _raise_multiple_detector_solutions_found(working_delta_nu_pairs)
        else:
            delta, nu = working_delta_nu_pairs[0]
            mu, eta, chi, phi = self._choose_sample_solution(mu_eta_chi_phi_tuples)
        return [(mu, delta, nu, eta, chi, phi)]

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
            V = CHI * PHI * N_phi * PSI.T * THETA.T                     # (56)

            xi = atan2(-V[2, 0], V[2, 2])
            eta = atan2(-V[0, 1], V[1, 1])
            mu = atan2(-V[2, 1], sqrt(V[2, 2] ** 2 + V[2, 0] ** 2))

        elif 'mu' in samp_constraints and 'eta' in samp_constraints:

            mu = samp_constraints['mu']
            eta = samp_constraints['eta']

            V = N_phi * PSI.T * THETA.T                                  # (49)

            bot = sqrt(sin(eta) ** 2 * cos(mu) ** 2 + sin(mu) ** 2)
            chi_orig = (asin(-V[2, 1] / bot) -
                   atan2(sin(mu), (sin(eta) * cos(mu))))                 # (52)

            # Choose final chi solution here to obtain compatable xi and mu
            # TODO: This temporary solution works only for one case used on i07
            #       Return a list of possible solutions?
            if is_small(eta) and is_small(mu + pi / 2):
                for chi in _generate_transformed_values(chi_orig):
                    if  pi / 2 <= chi < pi:
                        break
            else:
                chi = chi_orig

            a = sin(chi) * cos(eta)
            b = sin(chi) * sin(eta) * sin(mu) - cos(chi) * cos(mu)
            xi = atan2(V[2, 2] * a + V[2, 0] * b,
                       V[2, 0] * a - V[2, 2] * b)                        # (54)

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

        elif 'chi' in samp_constraints and 'mu' in samp_constraints:
            # derived in extensions_to_yous_paper.wxm
            chi = samp_constraints['chi']
            mu = samp_constraints['mu']

            if not is_small(mu) and not is_small(chi - pi / 2):
                raise Exception('The fixed chi, mu, psi/alpha/beta modes only '
                                ' currently work with chi=90 and mu=0')
            V = N_phi * PSI.T * THETA.T
            eta = asin(-V[2, 1])
            xi = atan2(V[2, 2], V[2, 0])
            phi = -atan2(V[0, 1], V[1, 1])

        else:
            raise DiffcalcException(
                'No code yet to handle this combination of 2 sample '
                'constraints and one reference!:' + str(samp_constraints))
        return xi, psi, mu, eta, chi, phi

    def _generate_detector_solutions(self, initial_delta, initial_nu, qaz,
                                        theta, det_constraint_name,
                                        filter_out_of_limits=True):
        if (ne(initial_delta, pi / 2) and
            (NUNAME not in self.constraints.detector)):
            if PRINT_DEGENERATE:
                print (('DEGENERATE: with delta=90, %s is degenerate: choosing '
                       '%s = 0 (allowed because %s is unconstrained)') %
                       (NUNAME, NUNAME, NUNAME))
            return ((initial_delta, 0), )  # delta, nu

        logger.info('initial detector solution - delta=% 7.3f, %s=% 7.3f',
                    initial_delta * TODEG, NUNAME, initial_nu * TODEG)
        possible_delta_nu_pairs = self._generate_possible_solutions(
            [initial_delta, initial_nu], ['delta', NUNAME],
            (det_constraint_name,), filter_out_of_limits)
        delta_nu_pairs = _filter_detector_solutions_by_theta_and_qaz(
            possible_delta_nu_pairs, theta, qaz)

        # When delta and mu are close to 90, two solutions for mu just below
        # and just above 90 may be found that fit theta to the specified
        # accuracy. In this case choose only the better of the two.
        pairs_close_to_90 = []
        other_pairs = []
        if len(delta_nu_pairs) > 1:
            for delta_, nu_ in delta_nu_pairs:
                if abs(delta_ - pi / 2) < .01 and abs(delta_ - pi / 2):
                    pairs_close_to_90.append((delta_, nu_))
                else:
                    other_pairs.append((delta_, nu_))
            if pairs_close_to_90:

                thetas_ = [_theta_and_qaz_from_detector_angles(delta_, nu_)[0]
                           for delta_, nu_ in pairs_close_to_90]
                th_errs = [abs(t - theta) for t in thetas_]
                closest_index = min(enumerate(th_errs), key=lambda x: x[1])[0]
                delta_nu_pairs = (other_pairs +
                                  [pairs_close_to_90[closest_index]])
        delta_nu_pairs = merge_nearly_equal_pairs(delta_nu_pairs)
        return delta_nu_pairs

    
    def _generate_sample_solutions(
            self, mu_, eta_, chi_, phi_, sample_constraint_names, delta, nu,
            wavelength, hkl, ref_constraint_name, ref_constraint_value,
            filter_out_of_limits=True):

        logger.info(
            'initial sample solution -- mu=% 7.3f, eta=% 7.3f, chi=% 7.3f, '
            'phi=% 7.3f', mu_ * TODEG, eta_ * TODEG, chi_ * TODEG,
            phi_ * TODEG)
        possible_tuples = self._generate_possible_solutions(
            [mu_, eta_, chi_, phi_], ['mu', 'eta', 'chi', 'phi'],
            sample_constraint_names, filter_out_of_limits)
        mu_eta_chi_phi_tuples = self._filter_valid_sample_solutions(
            delta, nu, possible_tuples, wavelength, hkl, ref_constraint_name,
            ref_constraint_value)
        return mu_eta_chi_phi_tuples

    def _filter_valid_sample_solutions(
        self, delta, nu, possible_mu_eta_chi_phi_tuples, wavelength, hkl,
        ref_constraint_name, ref_constraint_value):
        mu_eta_chi_phi_tuples = []

        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Checking all sample solutions (found to be within limits)\n'

        for mu, eta, chi, phi in possible_mu_eta_chi_phi_tuples:
            pos = YouPosition(mu, delta, nu, eta, chi, phi)
            hkl_actual = self._anglesToHkl(pos, wavelength)
            hkl_okay = sequence_ne(hkl, hkl_actual)

            if hkl_okay:
                virtual_angles = self._anglesToVirtualAngles(pos, wavelength)
                if not ref_constraint_name:
                    virtual_okay = True;
                elif ref_constraint_name == 'a_eq_b':
                    virtual_okay = ne(virtual_angles['alpha'],
                                      virtual_angles['beta'])
                else:
                    virtual_okay = ne(ref_constraint_value,
                                      virtual_angles[ref_constraint_name])
            else:
                virtual_okay = False
            if hkl_okay and virtual_okay:
                mu_eta_chi_phi_tuples.append((mu, eta, chi, phi))

            if logger.isEnabledFor(logging.DEBUG):
                msg += '*' if virtual_okay else '.'
                msg += '*' if hkl_okay else '.'
                msg += ('mu=% 7.10f, eta=% 7.10f, chi=% 7.10f, phi=% 7.10f' %
                        (mu * TODEG, eta * TODEG, chi * TODEG, phi * TODEG))
                if hkl_okay:
                    virtual_angles_in_deg = {}
                    for k in virtual_angles:
                        virtual_angles_in_deg[k] = virtual_angles[k] * TODEG
                    msg += (' --- psi=%(psi) 7.3f, tau=%(tau) 7.3f, '
                            'naz=%(naz) 7.3f, qaz=%(qaz) 7.3f, alpha=%(alpha) '
                            '7.3f, beta=%(beta) 7.3f' % virtual_angles_in_deg)
                msg += 'hkl= ' + str(hkl_actual)
                msg += '\n'
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(msg)
        return mu_eta_chi_phi_tuples

    def _choose_detector_solution(self, delta_nu_pairs):
        assert delta_nu_pairs, "delta_nu_pairs is empty"
        if len(delta_nu_pairs) > 1:
            _raise_multiple_detector_solutions_found(delta_nu_pairs)
        return delta_nu_pairs[0]

        


    def _choose_sample_solution(self, mu_eta_chi_phi_tuples):
        assert mu_eta_chi_phi_tuples, "mu_eta_chi_phi_tuples is empty"

        if len(mu_eta_chi_phi_tuples) == 1:
            return mu_eta_chi_phi_tuples[0]

        # there are multiple solutions
        absolute_distances = []
        for solution in mu_eta_chi_phi_tuples:
            absolute_distances.append(sum([abs(v) for v in solution]))

        shortest_solution_index = absolute_distances.index(
            min(absolute_distances))
        mu_eta_chi_phi = mu_eta_chi_phi_tuples[shortest_solution_index]

        if logger.isEnabledFor(logging.INFO):
            msg = ('Multiple sample solutions found (choosing solution with '
                   'shortest distance to all-zeros position):\n')
            i = 0
            for solution, distance in zip(mu_eta_chi_phi_tuples,
                                          absolute_distances):
                msg += '*' if i == shortest_solution_index else '.'

                values_in_deg = tuple(v * TODEG for v in solution)
                msg += ('mu=% 7.3f, eta=% 7.3f, chi=% 7.3f, phi=% 7.3f' %
                        values_in_deg)
                msg += ' (distance=% 4.3f)\n' % (distance * TODEG)
                i += 1
            msg += ':\n'
            logger.info(msg)

        return mu_eta_chi_phi

    def _generate_possible_solutions(self, values, names, constrained_names,
                                     filter_out_of_limits=True):

        # Expand each value into a list of values
        transformed_values = []
        for value, name in zip(values, names):
            transformed_values.append([])
            if name in constrained_names:
                transformed_values[-1].append(cut_at_minus_pi(value))
            else:             
                for transformed_value in _generate_transformed_values(value, False):
                    in_limits = self._hardware.is_axis_value_within_limits(name,
                        self._hardware.cut_angle(name, transformed_value * TODEG))
                    if in_limits or not filter_out_of_limits:
                        transformed_values[-1].append(cut_at_minus_pi(transformed_value))

        # Generate all combinations of the transformed values
        def expand(tuples_so_far, b):
            r = []
            for tuple_so_far in tuples_so_far:
                try:
                    tuple_so_far = tuple(tuple_so_far)
                except TypeError:
                    tuple_so_far = (tuple_so_far,)
                for bb in b:
                    new = tuple_so_far + (bb,)
                    r.append(new)
            return r

        return reduce(expand, transformed_values)

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
    
    # TODO: This special case should be *removed* when the gernal case has shown
    # toencompass it. It exists as fallback for a particular i16 experiment in
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


def _raise_multiple_detector_solutions_found(delta_nu_pairs):
    assert len(delta_nu_pairs) > 1
    delta_nu_pairs_degrees = [[v * TODEG for v in pair]
                                  for pair in delta_nu_pairs]
    raise DiffcalcException(
        'Multiple detector solutions were found: delta, %s = %s, '
        'please constrain detector limits' % (NUNAME, delta_nu_pairs_degrees))