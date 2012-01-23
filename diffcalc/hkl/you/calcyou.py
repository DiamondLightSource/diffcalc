from diffcalc.hkl.calcbase import HklCalculatorBase
from diffcalc.utils import DiffcalcException, bound, cross3, calcMU, calcPHI, \
    Position, angle_between_vectors, createYouMatrices
from math import pi, sin, cos, tan, acos, atan2, asin, sqrt
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
from diffcalc.configurelogging import logging

logger = logging.getLogger("diffcalc.hkl.you.calcyou")
I = Matrix.identity(3, 3)

SMALL = 1e-8
TORAD = pi / 180
TODEG = 180 / pi

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

def cut_at_minus_pi(value):
    if value < (-pi - SMALL):
        return value + 2 * pi
    if value >= pi + SMALL:
        return value - 2 * pi
    return value

def _calc_N(Q, n):
    """Return N as described by Equation 31"""
    Q = Q.times(1 / Q.normF())
    n = n.times(1 / n.normF())
    if is_small(angle_between_vectors(Q, n)):
        raise ValueError(
"Q and n are parallel and cannot be used to create an orthonormal matrix")
    Qxn = cross3(Q, n)
    QxnxQ = cross3(Qxn, Q)
    QxnxQ = QxnxQ.times(1 / QxnxQ.normF())
    Qxn = Qxn.times(1 / Qxn.normF())
    return Matrix([[Q.get(0, 0), QxnxQ.get(0, 0), Qxn.get(0, 0)],
                   [Q.get(1, 0), QxnxQ.get(1, 0), Qxn.get(1, 0)],
                   [Q.get(2, 0), QxnxQ.get(2, 0), Qxn.get(2, 0)]])

def _calc_angle_between_naz_and_qaz(theta, alpha, tau):
    # Equation 30:
    top = cos(tau) - sin(alpha) * sin(theta)
    bottom = cos(alpha) * cos(theta)
    if is_small(bottom):
        raise ValueError(
"Either cos(alpha) or cos(theta) are too small. This should have been caught by now")
    return acos(bound(top / bottom))    

def youAnglesToHkl(pos, wavelength, UBMatrix):
    """Calculate miller indices from position in radians."""
    
    [MU, DELTA, NU, ETA, CHI, PHI] = createYouMatrices(*pos.totuple())
    # Equation 12: Compute the momentum transfer vector in the lab  frame
    q_lab = ((NU.times(DELTA)).minus(I)).times(Matrix([[0], [2 * pi / wavelength], [0]]))
    # Transform this into the reciprocal lattice frame. 
    hkl = UBMatrix.inverse().times(PHI.inverse()).times(CHI.inverse()).times(
          ETA.inverse()).times(MU.inverse()).times(q_lab)
    
    return hkl.get(0, 0), hkl.get(1, 0), hkl.get(2, 0)    


def _tidy_degenerate_solutions(pos):
    
    original = pos.inDegrees()
    if is_small(pos.mu) and is_small(pos.nu): # assume a vertical 4-circle like mode
        if is_small(pos.chi): # phi || eta
            desired_eta = pos.delta / 2. 
            eta_diff = desired_eta - pos.eta
            pos.eta += eta_diff
            pos.phi -= eta_diff
            print "DEGENERATE: with chi=0, phi and eta are colinear: choosing eta = delta/2 by adding % 7.3f to eta and removing it from phi. (mu=nu=0 only)" % (eta_diff * TODEG,)
            print "            original:", original
    elif is_small(pos.delta) and is_small(pos.eta): # assume a horizontal 4-circle like mode
        if is_small(pos.chi-pi/2): # phi || eta
            desired_mu = pos.nu / 2. 
            mu_diff = desired_mu - pos.mu
            pos.mu += mu_diff
            pos.phi += mu_diff
            print "DEGENERATE: with chi=90, phi and mu are colinear: choosing mu = nu/2 by adding % 7.3f to mu and to phi. (delta=eta=0 only)" % (mu_diff * TODEG,)
            print "            original:", original
    
    return pos

def _theta_and_qaz_from_detector_angles(delta, nu):
    # Equation 19:
    cos_2theta = cos(delta) * cos(nu)
    theta = acos(bound(cos_2theta)) / 2.
    qaz = atan2(tan(delta), sin(nu))
    return theta, qaz

def _filter_detector_solutions_by_theta_and_qaz(possible_delta_nu_pairs, required_theta, required_qaz):
    delta_nu_pairs = []
    for delta, nu in possible_delta_nu_pairs:
        theta, qaz = _theta_and_qaz_from_detector_angles(delta, nu)
        if ne(theta, required_theta) and ne(qaz, required_qaz):
            delta_nu_pairs.append((delta, nu))
    return delta_nu_pairs
        



_identity_transform = lambda x: x

_transforms_for_general = (_identity_transform,
              lambda x :-x,
              lambda x : pi + x,
              lambda x : pi - x)

_transforms_for_zero = (lambda x : 0.,
                       lambda x : pi,)

_transforms_for_90_or_minus90 = (lambda x : pi/2,
                       lambda x : -pi/2,)

def _choose_transforms(value):
    if is_small(value):
        return _transforms_for_zero
    if is_small(value - pi / 2) or is_small(value + pi / 2):
        return _transforms_for_90_or_minus90
    return _transforms_for_general

class YouHklCalculator(HklCalculatorBase): 
    
    def __init__(self, ubcalc, geometry, hardware, constraints,
                  raiseExceptionsIfAnglesDoNotMapBackToHkl=True):
        HklCalculatorBase.__init__(self, ubcalc, geometry, hardware,
                                   raiseExceptionsIfAnglesDoNotMapBackToHkl)
        self._hardware = hardware # for checking limits only
        self.constraints = constraints
        
        self.n_phi = Matrix([[0], [0], [1]])
        """Reference vector in phi frame. Must be of length 1."""
        
    def repr_mode(self):
        return `self.constraints.all`
        
    def _anglesToHkl(self, pos, wavelength):
        """Calculate miller indices from position in radians."""
        return youAnglesToHkl(pos, wavelength, self._getUBMatrix())



    def _anglesToVirtualAngles(self, pos, wavelength):
        """Calculate pseudo-angles in radians from position in radians.
        
        Return theta, qaz, alpha, naz, tau, psi and beta in a dictionary.
        
        """
        
        del wavelength # TODO: not used
        
        # depends on surface normal n_lab.
        mu, delta, nu, eta, chi, phi = pos.totuple()

        # Equation 19:
        theta, qaz = _theta_and_qaz_from_detector_angles(delta, nu)
        
        #Equation 20:
        [MU, _, _, ETA, CHI, PHI] = createYouMatrices(mu,
                                           delta, nu, eta, chi, phi)
        Z = MU.times(ETA).times(CHI).times(PHI)
        n_lab = Z.times(self.n_phi)
        alpha = asin(bound((-n_lab.get(1, 0))))
        naz = atan2(n_lab.get(0, 0), n_lab.get(2, 0))
        
        #Equation 23:
        cos_tau = cos(alpha) * cos(theta) * cos(naz - qaz) + \
                  sin(alpha) * sin(theta)
        tau = acos(bound(cos_tau))
        
        # Compute Tau using the dot product directly (THIS ALSO WORKS)
#        q_lab = ( (NU.times(DELTA)).minus(I) ).times(Matrix([[0],[1],[0]]))
#        norm = q_lab.normF()
#        q_lab = Matrix([[1],[0],[0]]) if norm == 0 else q_lab.times(1/norm)
#        tau_from_dot_product = acos(bound(dot3(q_lab, n_lab)))
        
        # Equation 24:
        sin_beta = 2 * sin(theta) * cos(tau) - sin(alpha)
        beta = asin(bound(sin_beta))
        
        # Equation 28:
        sin_tau = sin(tau)
        cos_theta = cos(theta)       
        if sin_tau == 0:
            psi = float('Nan')
            print (
"""WARNING: Diffcalc could not calculate a unique azimuth (psi) as the scattering
vector (Q) and the reference vector (n) are parallel""")
        elif cos_theta == 0:
            psi = float('Nan')
            print (
"""WARNING: Diffcalc could not calculate a unique azimuth (psi) because the
scattering vector (Q) and xray beam are are parallel and don't form a unique
reference plane""")
        else:
            cos_psi = (cos(tau) * sin(theta) - sin(alpha)) / (sin_tau * cos_theta) 
            psi = acos(bound(cos_psi))    
        
        return {'theta': theta, 'qaz': qaz, 'alpha': alpha,
                'naz': naz, 'tau': tau, 'psi': psi, 'beta': beta}

    def _choose_detector_angles(self, delta_nu_pairs):
        if len(delta_nu_pairs) > 1:
            raise Exception("Multiple detector solutions were found: delta, nu = %s, please constrain detector limits" % delta_nu_pairs)
        if len(delta_nu_pairs) == 0:
            raise Exception("No detector solutions were found, please unconstrain detector limits")
        return delta_nu_pairs[0]
    

    def _choose_sample_angles(self, mu_eta_chi_phi_tuples):

        if len(mu_eta_chi_phi_tuples) == 0:
            raise Exception("No sample solutions were found, please un-constrain sample limits")
        
        if len(mu_eta_chi_phi_tuples) == 1:
            return mu_eta_chi_phi_tuples[0]
        
        # there are multiple solutions
        absolute_distances = []
        for solution in mu_eta_chi_phi_tuples:
            absolute_distances.append(sum([abs(v) for v in solution]))
            
        shortest_solution_index = absolute_distances.index(min(absolute_distances))
        mu_eta_chi_phi = mu_eta_chi_phi_tuples[shortest_solution_index]
        
        if logger.isEnabledFor(logging.INFO):
            msg = 'Multiple sample solutions found (choosing solution with shortest distance to all-zeros position):\n'
            i = 0
            for solution, distance in zip(mu_eta_chi_phi_tuples, absolute_distances):
                msg += '*' if i == shortest_solution_index else '.'
                    
                values_in_deg = tuple(v * TODEG for v in solution)
                msg += 'mu=% 7.3f, eta=% 7.3f, chi=% 7.3f, phi=% 7.3f' % values_in_deg
                msg += ' (distance=% 4.3f)\n' % (distance * TODEG)
                i += 1
            msg += ':\n'
            logger.info(msg)
        
        return mu_eta_chi_phi
    
    
    def _hklToAngles(self, h , k , l, wavelength):
        """(pos, virtualAngles) = hklToAngles(h, k, l, wavelength) --- with Position object 
        pos and the virtual angles returned in degrees. Some modes may not calculate
        all virtual angles.
        """
        # HINT: To help follow this code: know that none of the methods called within will
        # effect the state of the AngleCalculator object!!!
        
        h_phi = self._getUBMatrix().times(Matrix([[h], [k], [l]]))
        theta = self._calc_theta(h_phi, wavelength)
        tau = angle_between_vectors(h_phi, self.n_phi)
        
        ### Reference constraint column ###
        
        reference_constraint = self.constraints.reference
        if reference_constraint:
            # One of the angles for the reference vector (n) is given (Section 5.2)
            ref_constraint_name, ref_constraint_value = reference_constraint.items()[0]
            _, alpha, _ = self._calc_remaining_reference_angles_given_one(
                                ref_constraint_name, ref_constraint_value, theta, tau)
        else:
            raise RuntimeError("Code not yet written to handle the absence of a reference constraint!")
        
        ### Detector constraint column ###
        
        detector_constraint = self.constraints.detector      
        naz_constraint = self.constraints.naz
        assert not (detector_constraint and naz_constraint), (
               "Two 'detector' constraints given")
        
        if detector_constraint:
            # One of the detector angles is given (Section 5.1)
            det_constraint_name, det_constraint = detector_constraint.items()[0]
            delta, nu, qaz = self._calc_remaining_detector_angles_given_one(
                             det_constraint_name, det_constraint, theta)
            naz_qaz_angle = _calc_angle_between_naz_and_qaz(theta, alpha, tau)
            naz = qaz - naz_qaz_angle
#            if (naz < -SMALL) or (naz >= pi):
#                naz = qaz + naz_qaz_angle
                
        elif naz_constraint:
            # The 'detector' angle naz is given:
            det_constraint_name, det_constraint = naz_constraint.items()[0]
            naz_name, naz = det_constraint_name, det_constraint
            assert naz_name == 'naz'            
            naz_qaz_angle = _calc_angle_between_naz_and_qaz(theta, alpha, tau)
            qaz = naz - naz_qaz_angle
#            if (qaz < -SMALL) or (qaz >= pi):
#                qaz = naz + naz_qaz_angle
            nu = atan2(sin(2 * theta) * cos(qaz), cos(2 * theta))
            delta = atan2(sin(qaz) * sin(nu), cos(qaz))
            
        else:
            # No detector constraint is given 
            raise RuntimeError("No code yet to handle the absence of a detector constraint!")


        logger.info("initial detector solution - delta=% 7.3f, nu=% 7.3f" % (delta * TODEG, nu * TODEG))
        possible_delta_nu_pairs = self._generate_possible_detector_solutions(delta, nu, det_constraint_name)
        delta_nu_pairs = _filter_detector_solutions_by_theta_and_qaz(possible_delta_nu_pairs, theta, qaz)
        delta, nu = self._choose_detector_angles(delta_nu_pairs)
        
        
        ### Sample constraint column ###
         
        samp_constraints = self.constraints.sample
        
        if len(samp_constraints) == 1:
            # JUST ONE SAMPLE ANGLE GIVEN
            sample_constraint_name, sample_value = samp_constraints.items()[0]
            q_lab = Matrix([[cos(theta) * sin(qaz)],
                            [-sin(theta)],
                            [cos(theta) * cos(qaz)]]) # Equation 18
            n_lab = Matrix([[cos(alpha) * sin(naz)],
                            [-sin(alpha)],
                            [cos(alpha) * cos(naz)]]) # Equation 20
            
            phi, chi, eta, mu = self._calc_remaining_sample_angles_given_one(
                                     sample_constraint_name, sample_value, q_lab, n_lab, h_phi, self.n_phi)

        elif len(samp_constraints) == 2:
            raise DiffcalcException("No code yet to handle 2 sample constraints!")
        
        elif len(samp_constraints) == 3:
            raise DiffcalcException("No code yet to handle 3 sample constraints!")
        
        else:
            raise AssertionError('1,2 or 3 sample constraints expected, not: ',
                                  len(samp_constraints))
            

        logger.info("initial sample solution -- mu=% 7.3f, eta=% 7.3f, chi=% 7.3f, phi=% 7.3f" % (mu * TODEG, eta * TODEG, chi * TODEG, phi * TODEG))
        possible_mu_eta_chi_phi_tuples = self._generate_possible_sample_solutions(mu, eta, chi, phi, sample_constraint_name)
        mu_eta_chi_phi_tuples = self._filter_sample_solutions_by_hkl_and_virtual_angle(delta, nu, possible_mu_eta_chi_phi_tuples, wavelength, (h, k, l), ref_constraint_name, ref_constraint_value)
        mu, eta, chi, phi = self._choose_sample_angles(mu_eta_chi_phi_tuples)
        
        # Create position
        position = Position(mu, delta, nu, eta, chi, phi)
        position = _tidy_degenerate_solutions(position)
        if position.phi <= -pi + SMALL:
            position.phi += 2 * pi

        # pseudo angles calculated along the way were for the initial solution
        # and may be invalid for the chosen solution
        # TODO: anglesToHkl need no longer check the pseudo_angles as they will be
        # generated with the same function and it will prove nothing
        pseudo_angles = self._anglesToVirtualAngles(position, wavelength) 
        return position, pseudo_angles
                
    def _calc_theta(self, h_phi, wavelength):
        """Calculate theta using Equation1"""
        q_length = h_phi.normF()        
        if q_length == 0:
            raise DiffcalcException("Reflection is unreachable as |Q| is 0")
        wavevector = 2 * pi / wavelength
        try:
            theta = asin(q_length / (2 * wavevector))
        except ValueError:
            raise DiffcalcException("Reflection is unreachable as |Q| is too long")
        return theta
    
    def _generate_possible_detector_solutions(self, delta, nu, det_constraint_name):
        return self._generate_possible_solutions([delta, nu], ['delta', 'nu'], (det_constraint_name,))

    def _generate_possible_sample_solutions(self, mu, eta, chi, phi, sample_constraint_name):
        possible_mu_eta_chi_phi_tuples = self._generate_possible_solutions([mu, eta, chi, phi], ['mu', 'eta', 'chi', 'phi'], (sample_constraint_name,))
        return possible_mu_eta_chi_phi_tuples
    
    def _filter_sample_solutions_by_hkl_and_virtual_angle(self, delta, nu, possible_mu_eta_chi_phi_tuples, wavelength, hkl, ref_constraint_name, ref_constraint_value):
        mu_eta_chi_phi_tuples = []
        
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Checking all sample solutions (found to be within limits)\n'
          
        for mu, eta, chi, phi in possible_mu_eta_chi_phi_tuples:
            pos = Position(mu, delta, nu, eta, chi, phi)
            hkl_actual = self._anglesToHkl(pos, wavelength)
            hkl_okay = sequence_ne(hkl, hkl_actual)
 
            if hkl_okay:
                virtual_angles = self._anglesToVirtualAngles(pos, wavelength)
                if ref_constraint_name == 'a_eq_b':
                    virtual_okay = ne(virtual_angles['alpha'], virtual_angles['beta'])
                else:
                    virtual_okay = ne(ref_constraint_value, virtual_angles[ref_constraint_name])
            else:
                virtual_okay = False  
            if hkl_okay and virtual_okay:
                mu_eta_chi_phi_tuples.append((mu, eta, chi, phi))
                
                
            if logger.isEnabledFor(logging.DEBUG):
                msg += '*' if virtual_okay else '.'
                msg += '*' if hkl_okay else '.'
                msg += 'mu=% 7.10f, eta=% 7.10f, chi=% 7.10f, phi=% 7.10f' % (mu * TODEG, eta * TODEG, chi * TODEG, phi * TODEG)
                if hkl_okay:
                    virtual_angles_in_deg = {}
                    for k in virtual_angles:
                        virtual_angles_in_deg[k] = virtual_angles[k] * TODEG
                        #         return {'theta': theta, 'qaz': qaz, 'alpha': alpha, 'naz': naz, 'tau': tau, 'psi': psi, 'beta': beta}
                    msg += ' --- psi=%(psi) 7.3f, tau=%(tau) 7.3f, naz=%(naz) 7.3f, qaz=%(qaz) 7.3f, alpha=%(alpha) 7.3f, beta=%(beta) 7.3f' % virtual_angles_in_deg
                msg += '\n'
        if logger.isEnabledFor(logging.DEBUG): 
            logger.debug(msg)
        return mu_eta_chi_phi_tuples

    
    def _calc_remaining_reference_angles_given_one(self, name, value, theta, tau):
        """Return psi, alpha and beta given one of a_eq_b, alpha, beta or psi"""
        if sin(tau) == 0:
            raise DiffcalcException(
"""The constraint %s could not be used to determine a unique azimuth (psi) as
the scattering vector (Q) and the reference vector (n) are parallel""" % name)
        if cos(theta) == 0:
            raise DiffcalcException(
"""The constraint %s could not be used to determine a unique azimuth (psi) as
the scattering vector (Q) and xray beam are are parallel and don't form a unique
reference plane""" % name)

        if name == 'psi':
            psi = value
            # Equation 26 for alpha
            sin_alpha = cos(tau) * sin(theta) - cos(theta) * sin(tau) * cos(psi)
            if abs(sin_alpha) > 1 + SMALL:
                raise DiffcalcException(
                 "No reflection can be reached where psi = %.4f." % psi)
            alpha = asin(bound(sin_alpha))
            # Equation 27 for beta
            sin_beta = cos(tau) * sin(theta) + cos(theta) * sin(tau) * cos(psi)
            if abs(sin_beta) > 1 + SMALL:
                raise DiffcalcException(
                 "No reflection can be reached where psi = %.4f." % psi)
            beta = asin(bound(sin_beta))
        elif name == 'a_eq_b':
            # Equation 24
            alpha = beta = asin(bound(cos(tau) * sin(theta)))
        elif name == 'alpha':
            # Equation 24
            alpha = value
            sin_beta = 2 * sin(theta) * cos(tau) - sin(alpha)
            beta = asin(sin_beta)
        elif name == 'beta':
            # Equation 24
            beta = value
            sin_alpha = 2 * sin(theta) * cos(tau) - sin(beta)
            if abs(sin_alpha) > 1 + SMALL:
                raise DiffcalcException(
                 "No reflection can be reached where beta = %.4f." % beta)
            alpha = asin(sin_alpha)
        
        if name != 'psi':
            cos_psi = (cos(tau) * sin(theta) - sin(alpha)) / (sin(tau) * cos(theta))
            psi = acos(bound(cos_psi))
            
        return psi, alpha, beta

    def _calc_remaining_detector_angles_given_one(self, constraint_name, constraint_value, theta):
        """Return delta, nu and qaz given one detector angle (from section 5.1)."""
        
        # Find qaz using various derivations of 17 and 18
        if constraint_name == 'delta':
            delta = constraint_value
            # Equation 17 and 18 (x components are equal)
            sin_2theta = sin(2 * theta)
            if is_small(sin_2theta):
                raise DiffcalcException(
"""No meaningful scattering vector (Q) can be found when theta=%.4f.
(sin(2theta) is too small.)""" % theta)
            qaz = asin(bound(sin(delta) / sin_2theta))
        
        elif constraint_name == 'nu':
            nu = constraint_value
#            cos_delta = cos(2*theta) / cos(nu)#<--fails when nu = 90 
#            delta = acos(bound(cos_delta))
#            tan
            sin_2theta = sin(2 * theta)
            if is_small(sin_2theta):
                raise DiffcalcException(
"""No meaningful scattering vector (Q) can be found when theta=%.4f.
(sin(2theta) is too small.)""" % theta)
            cos_qaz = tan(nu) / tan(2 * theta)
            if abs(cos_qaz) > 1 + SMALL:
                raise DiffcalcException(
"The specified nu=%.4f is greater than the 2theta (%.4f)" % (nu, theta))
            qaz = acos(bound(cos_qaz));
            
        elif constraint_name == 'qaz':
            qaz = constraint_value
        
        else:
            raise ValueError(constraint_name + 
              " is not an explicit detector angle (naz cannot be handled here)")
        
        if constraint_name != 'nu':
            # TODO: does this calculation of nu suffer the same problems as
            #       that of delta below
            nu = atan2(sin(2 * theta) * cos(qaz), cos(2 * theta))
        
        if constraint_name != 'delta':
            cos_qaz = cos(qaz)
            if not is_small(cos_qaz): # TODO: could we switch methods at 45 deg
                delta = atan2(sin(qaz) * sin(nu), cos_qaz)
            else:
                # qaz is close to 90 (a common place for it!
                delta = sign(qaz) * acos(bound(cos(2 * theta) / cos(nu)))
        
        return delta, nu, qaz
    
    def _calc_remaining_sample_angles_given_one(self, constraint_name, constraint_value, q_lab, n_lab,
                                                q_phi, n_phi):
        """Return phi, chi, eta and mu, given one of these (from section 5.3)."""
        # TODO: Sould return a valid solution, rather than just one that can
        # be mapped to a correct solution by applying +-x and 180+-x mappings
        
        N_lab = _calc_N(q_lab, n_lab)
        N_phi = _calc_N(q_phi, n_phi)
        
        if constraint_name == 'mu': # Equation 35.
            mu = constraint_value
            V = calcMU(mu).inverse().times(N_lab).times(N_phi.transpose()).array
            phi = atan2(V[2][1], V[2][0])
            eta = atan2(-V[1][2], V[0][2])
            chi = atan2(sqrt(V[2][0] ** 2 + V[2][1] ** 2), V[2][2]) # -pi/2<chi< pi/2
            if is_small(sin(chi)): # chi ~= 0 or 180 and therefor phi || eta
                # The solutions for phi and eta here will be valid but will be
                # chosen unpredictably. Choose eta=0:
                phi_orig, eta_orig = phi, eta
                # tan(phi+eta)=v12/v11 from docs/extensions_to_yous_paper.wxm
                eta = 0
                phi = atan2(V[0][1], V[0][0])
                logger.debug(
"""Eta and phi cannot be chosen uniquely with chi so close to 0 or 180. Ignoring
solution phi=%.3f and eta=%.3, and returning phi=%.3f and eta=%.3""",
                    phi_orig*TODEG, eta_orig*TODEG, phi*TODEG, eta*TODEG  )
            return phi, chi, eta, mu
        
        if constraint_name == 'phi': # Equation 37
            phi = constraint_value
            V = N_lab.times(N_phi.inverse()).times(calcPHI(phi).transpose()).array
            eta = atan2(V[0][1], sqrt(V[1][1] ** 2 + V[2][1] ** 2))
            mu = atan2(V[2][1], V[1][1])
            chi = atan2(V[0][2], V[0][0]) # -pi/2 < chi < pi/2
            if is_small(cos(eta)):
                #TODO: Not likely to happen in real world!?
                raise ValueError(
"""Chi and mu cannot be chosen uniquely with eta so close to +-90.
(The chi ring would block the beam anyway).""")
            return phi, chi, eta, mu 
        
        elif constraint_name in ('eta', 'chi'):
            V = N_lab.times(N_phi.transpose()).array
            if constraint_name == 'eta': # Equation 39
                eta = constraint_value
                cos_eta = cos(eta)
                if is_small(cos_eta):
                    #TODO: Not likely to happen in real world!?
                    raise ValueError(
"""Chi and mu cannot be chosen uniquely with eta constrained so close to +-90.
(The chi ring would block the beam anyway)""")
                chi = asin(V[0][2] / cos_eta) # -pi/2 < chi < pi/2
            else: # constraint_name == 'chi', Equation 40
                chi = constraint_value
                sin_chi = sin(chi)
                if is_small(sin_chi):
                    raise ValueError(
""""Eta and phi cannot be chosen uniquely with chi constrained so close to 0.
(Please contact developer if this case is actually useful for you)""")
                eta = acos(V[0][2] / sin_chi)
            # Equation 41:
            top_for_mu = V[2][2] * sin(eta) * sin(chi) + V[1][2] * cos(chi)
            bot_for_mu = -V[2][2] * cos(chi) + V[1][2] * sin(eta) * sin(chi)
            mu = atan2(-top_for_mu, -bot_for_mu) # minus signs added from paper to pass (pieces) tests
            if is_small(top_for_mu) and is_small(bot_for_mu): 
                # chi == +-90, eta == 0/180 and therefor phi || mu
                # cos(chi) == 0 and sin(eta) == 0
                # Experience shows that even though e.g. the V[2][2] and V[1][2]
                # values used to calculate mu may be basically 0 (1e-34) their
                # ratio in every case tested so far still remains valid and
                # using them will result in a phi solution that is continous
                # with neighbouring positions.
                #
                # We cannot test phi minus mu here unfortunetely as the final phi
                # and mu solutions have not yet been chosen (they may be +-x or 180+-x).
                # Otherwise we could choose a sensible solution here if the one found was incorrect.
                                                
                # tan(phi+eta)=v12/v11 from extensions_to_yous_paper.wxm
                phi_minus_mu = -atan2(V[2][0],V[1][1])
                logger.debug(
"""Mu and phi cannot be chosen uniquely with chi so close to +-90 and eta so close 0 or 180.
After the final solution has been chose phi-mu should equal: %.3f""", phi_minus_mu*TODEG  )
            # Eqution 42:
            top_for_phi = V[0][1] * cos(eta) * cos(chi) - V[0][0] * sin(eta)
            bot_for_phi =  V[0][1] * sin(eta) + V[0][0] * cos(eta) * cos(chi)
            phi = atan2(top_for_phi, bot_for_phi)
#            if is_small(bot_for_phi) and is_small(top_for_phi):
#                raise ValueError(
#"phi=%.3f cannot be known with confidence as top an bottom are both close to zero. chi=%.3f, eta=%.3f"%(mu*TODEG, chi*TODEG, eta*TODEG))
            return phi, chi, eta, mu
        
        raise ValueError('Given angle must be one of phi, chi, eta or mu')

    def _generate_possible_solutions(self, values, names, constrained_names):
        
        individualy_transformed_values = []
        for value, name in zip(values, names):
            transforms_of_value_within_limits = []
            transforms = (_identity_transform,) if name in constrained_names else _choose_transforms(value)
            for transform in transforms:
                transformed_value = transform(value)
                if self._hardware.isAxisValueWithinLimits(name,
                        self._hardware.cutAngle(name, transformed_value * TODEG)):
                    transforms_of_value_within_limits.append(cut_at_minus_pi(transformed_value))
            individualy_transformed_values.append(transforms_of_value_within_limits)
    
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
        
        return reduce(expand, individualy_transformed_values)
