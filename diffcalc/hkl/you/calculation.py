from math import pi, sin, cos, tan, acos, atan2, asin, sqrt, atan

from diffcalc.utils import DiffcalcException, bound, dot3, cross3, calcMU,\
    calcPHI, Position, angle_between_vectors
from diffcalc.utils import createYouMatrices
from diffcalc.hkl.calcbase import HklCalculatorBase
from diffcalc.hkl.you.constraints import ConstraintManager
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

I = Matrix.identity(3,3)

SMALL = 1e-8
TORAD=pi/180
TODEG=180/pi

def is_small(x):
    return abs(x) < SMALL

def sign(x):
    return 1 if x>0 else -1




def _calc_N(Q, n):
    """Return N as described by Equation 31"""
    Q = Q.times(1/Q.normF())
    n = n.times(1/n.normF())
    if is_small(angle_between_vectors(Q, n)):
        raise ValueError(
"Q and n are parallel and cannot be used to create an orthonormal matrix")
    QxnxQ = cross3(Q, cross3(n, Q)) # order independent given this symmetry
    Qxn = cross3(Q, n)
    QxnxQ = QxnxQ.times(1/QxnxQ.normF())
    Qxn = Qxn.times(1/Qxn.normF())
    return Matrix([[Q.get(0,0), QxnxQ.get(0,0), Qxn.get(0,0)],
                   [Q.get(1,0), QxnxQ.get(1,0), Qxn.get(1,0)],
                   [Q.get(2,0), QxnxQ.get(2,0), Qxn.get(2,0)]])

def _calc_angle_between_naz_and_qaz(theta, alpha, tau):
    # Equation 30:
    top = cos(tau) - sin(alpha)*sin(theta)
    bottom = cos(alpha)*cos(theta)
    if is_small(bottom):
        raise Exception(
"Either cos(alpha) or cos(theta) are too small. This should have been caught by now")
    return acos(bound(top/bottom))    

def youAnglesToHkl(pos, energy, UBMatrix):
    """Calculate miller indices from position in radians."""
    try:
        wavelength = 12.39842 / energy
    except ZeroDivisionError:
        raise DiffcalcException("Cannot calculate hkl position as energy is 0")
    
    [MU, DELTA, NU, ETA, CHI, PHI] = createYouMatrices(*pos.totuple())
    # Equation 12: Compute the momentum transfer vector in the lab  frame
    q_lab = ((NU.times(DELTA)).minus(I)).times(Matrix([[0],[2*pi/wavelength],[0]]))
    # Transform this into the reciprocal lattice frame. 
    hkl = UBMatrix.inverse().times(PHI.inverse()).times(CHI.inverse()).times(
          ETA.inverse()).times(MU.inverse()).times(q_lab)
    
    return hkl.get(0, 0), hkl.get(1, 0), hkl.get(2, 0)    


class YouHklCalculator(HklCalculatorBase): 
    
    def __init__(self,  ubcalc, geometry, hardware,
                  raiseExceptionsIfAnglesDoNotMapBackToHkl = False):
        HklCalculatorBase.__init__(self, ubcalc, geometry, hardware, 
                                   raiseExceptionsIfAnglesDoNotMapBackToHkl)
        
        self.constraints = ConstraintManager()
        
        self.n_phi = Matrix([[0],[0],[1]])
        """Reference vector in phi frame. Must be of length 1."""
        
        self.choose_chi_from_0_to_pi = False # default is -pi/2<chi<pi/2
        
        
        
    def _anglesToHkl(self, pos, energy):
        """Calculate miller indices from position in radians."""
        return youAnglesToHkl(pos, energy, self._getUBMatrix())

    def _anglesToVirtualAngles(self, pos, energy):
        """Calculate pseudo-angles in radians from position in radians.
        
        Return theta, qaz, alpha, naz, tau, psi and beta in a dictionary.
        
        """
        # depends on surface normal n_lab.
        mu, delta, nu, eta, chi, phi = pos.totuple()

        
        # Equation 19:
        cos_2theta = cos(delta) * cos(nu)
        theta = acos(bound(cos_2theta)) / 2.
        qaz = atan2(tan(delta), sin(nu))
        
        #Equation 20:
        [MU, _, _, ETA, CHI, PHI] = createYouMatrices(mu,
                                           delta, nu, eta, chi, phi)
        Z = MU.times(ETA).times(CHI).times(PHI)
        n_lab = Z.times(self.n_phi)
        alpha = asin(bound((-n_lab.get(1,0))))
        naz = atan2(n_lab.get(0,0), n_lab.get(2,0))
        
        #Equation 23:
        cos_tau = cos(alpha) * cos(theta) * cos(naz-qaz) + \
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
        

    def _hklToAngles(self,h ,k ,l, energy):
        """(pos, virtualAngles) = hklToAngles(h, k, l, energy) --- with Position object 
        pos and the virtual angles returned in degrees. Some modes may not calculate
        all virtual angles.
        """
        # HINT: To help follow this code: know that none of the methods called within will
        # effect the state of the AngleCalculator object!!!

        
        h_phi = self._getUBMatrix().times(Matrix([[h], [k], [l]]))
        theta = self._calc_theta(h_phi, 12.39842 / energy)
        tau = angle_between_vectors(h_phi, self.n_phi)
        
        ### Reference constraint column ###
        
        reference_constraint = self.constraints.reference
        if reference_constraint:
            # One of the angles for the reference vector (n) is given (Section 5.2)
            ref_name, ref_value = reference_constraint.items()[0]
            psi, alpha, beta = self._calc_remaining_reference_angles_given_one(
                                ref_name, ref_value, theta, tau)
        else:
            raise RuntimeError("Code not yet written to handle the absense of a reference constraint!")
             
        
        ### Detector constraint column ###
        
        detector_constraint = self.constraints.detector      
        naz_constraint = self.constraints.naz
        assert not (detector_constraint and naz_constraint), (
               "Two 'detector' constraints given")
        
        if detector_constraint:
            # One of the detector angles is given (Section 5.1)
            det_name, det_constraint = detector_constraint.items()[0]
            delta, nu, qaz = self._calc_remaining_detector_angles_given_one(
                             det_name, det_constraint, theta)
            naz_qaz_angle = self._calc_angle_between_naz_and_qaz(theta, alpha, tau)
            naz = qaz - naz_qaz_angle
            if (naz < -SMALL) or (naz >= pi):
                naz = qaz + naz_qaz_angle
                
        elif naz_constraint:
            # The 'detector' angle naz is given:
            naz_name, naz = naz_constraint.items()[0]
            assert naz_name == 'naz'            
            naz_qaz_angle = self._calc_angle_between_naz_and_qaz(theta, alpha, tau)
            qaz = naz - naz_qaz_angle
            if (qaz < -SMALL) or (qaz >= pi):
                qaz = naz + naz_qaz_angle
            nu = atan2(sin(2*theta)*cos(qaz), cos(2*theta))
            delta = atan2(sin(qaz)*sin(nu), cos(qaz))
            
        else:
            # No detector contraint is given 
            raise RuntimeError("No code yet to handle the absense of a detector constraint!")

        ### Sample constraint columns ###
        
        samp_constraints = self.constraints.sample
        
        if len(samp_constraints) == 0:
            raise AssertionError('1,2 or 3 sample constraints expected, not: 0')
        
        elif len(samp_constraints) == 1:
            # JUST ONE SAMPLE ANGLE GIVEN
            sample_name, sample_value = samp_constraints.items()[0]
            q_lab = Matrix([[cos(theta)*sin(qaz)],
                            [-sin(theta)],
                            [cos(theta)*cos(qaz)]]) # Equation 18
            n_lab = Matrix([[cos(alpha)*sin(naz)],[],[]])
            # Check this is true and get it
            
            sample_name, sample_value = self.constraints.sample
            phi, chi, eta, mu = self._calc_remaining_sample_angles_given_one(
                                     sample_name, sample_value, q_lab, n_lab, h_phi, self.n_phi)

        elif len(samp_constraints) == 2:
            raise DiffcalcException("No code yet to handle 2 sample constraints!")
        
        elif len(samp_constraints) == 3:
            raise DiffcalcException("No code yet to handle 3 sample constraints!")
        
        else:
            raise AssertionError('1,2 or 3 sample constraints expected, not: ',
                                  len(samp_constraints))
            
        ### Finished! ###
        
        position = Position(mu, delta, nu, eta, chi, phi)
        pseudo_angles = {'theta': theta, 'qaz': qaz, 'alpha': alpha,
                         'naz': naz, 'tau': tau, 'psi': psi, 'beta': beta}
        return position, pseudo_angles
                
    def _calc_theta(self, h_phi, wavelength):
        """Calculate theta using Equation1"""
        q_length = h_phi.normF()        
        if q_length == 0:
            raise DiffcalcException("Reflection is unreachable as |Q| is 0")
        wavevector = 2*pi/wavelength
        try:
            theta = asin(q_length / (2*wavevector))
        except ValueError:
            raise DiffcalcException("Reflection is unreachable as |Q| is too long")
        return theta
    
    def _calc_remaining_reference_angles_given_one(self, name, value, theta, tau):
        """Return psi, alpha and beta given one of alpha_equal_beta, alpha, beta or psi"""
        
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
            sin_alpha = cos(tau)*sin(theta) - cos(theta)*sin(tau)*cos(psi)
            if abs(sin_alpha) > 1+SMALL:
                raise DiffcalcException(
                 "No reflection can be reached where psi = %.4f." % psi)
            alpha = asin(bound(sin_alpha))
            # Equation 27 for beta
            sin_beta = cos(tau)*sin(theta) + cos(theta)*sin(tau)*cos(psi)
            if abs(sin_beta) > 1+SMALL:
                raise DiffcalcException(
                 "No reflection can be reached where psi = %.4f." % psi)
            beta = asin(bound(sin_beta))
        elif name == 'alpha_equal_beta':
            # Equation 24
            alpha = beta = asin(bound(cos(tau) * sin(theta)))
        elif name == 'alpha':
            # Equation 24
            alpha = value
            sin_beta = 2*sin(theta)*cos(tau) - sin(alpha)
            beta = asin(sin_beta)
        elif name == 'beta':
            # Equation 24
            beta = value
            sin_alpha = 2*sin(theta)*cos(tau) - sin(beta)
            if abs(sin_alpha) > 1+SMALL:
                raise DiffcalcException(
                 "No reflection can be reached where beta = %.4f." % beta)
            alpha = asin(sin_alpha)
        
        if name != 'psi':
            cos_psi = (cos(tau)*sin(theta) - sin(alpha)) / (sin(tau)*cos(theta))
            psi = acos(bound(cos_psi))
            
        return psi, alpha, beta

    def _calc_remaining_detector_angles_given_one(self, name, value, theta):
        """Return delta, nu and qaz given one detector angle (from section 5.1)."""
        
        # Find qaz using various derivations of 17 and 18
        if name == 'delta':
            delta = value
            # Equation 17 and 18 (x components are equal)
            sin_2theta = sin(2*theta)
            if is_small(sin_2theta):
                raise DiffcalcException(
"""No meaningful scattering vector (Q) can be found when theta=%.4f.
(sin(2theta) is too small.)""" % theta)
            qaz = asin(bound(sin(delta) / sin_2theta))
        
        elif name == 'nu':
            nu = value
#            cos_delta = cos(2*theta) / cos(nu)#<--fails when nu = 90 
#            delta = acos(bound(cos_delta))
#            tan
            sin_2theta = sin(2*theta)
            if is_small(sin_2theta):
                raise DiffcalcException(
"""No meaningful scattering vector (Q) can be found when theta=%.4f.
(sin(2theta) is too small.)""" % theta)
            cos_qaz = tan(nu) / tan(2*theta)
            if abs(cos_qaz) > 1 + SMALL:
                raise DiffcalcException(
"The specified nu=%.4f is greater than the 2theta (%.4f)" % (nu,theta))
            qaz = acos(bound(cos_qaz));
            
        elif name == 'qaz':
            qaz = value
        
        else:
            raise ValueError(name +
              " is not an explicit detector angle (naz cannot be handled here)")
        
        if name != 'nu':
            # TODO: does this calculation of nu suffer the same problems as
            #       that of delta below
            nu = atan2(sin(2*theta)*cos(qaz), cos(2*theta))
        
        if name != 'delta':
            print "qaz: ", qaz
            print "nu: ", nu
            cos_qaz =  cos(qaz)
            if not is_small(cos_qaz): # TODO: could we switch methods at 45 deg
                delta = atan2(sin(qaz)*sin(nu), cos_qaz)
            else:
                # qaz is close to 90 (a common place for it!
                delta = sign(qaz) * acos(bound(cos(2*theta) / cos(nu)))
        
        return delta, nu, qaz
    
    

            
            
    
    def _calc_remaining_sample_angles_given_one(self, name, value, Q_lab, n_lab,
                                                Q_phi,  n_phi):
        """Return phi, chi, eta and mu, given one of these (from section 5.3)."""
        
        #TODO: Check this whole code for special cases!!!!
        
        N_lab = _calc_N(Q_lab, n_lab)
        N_phi = _calc_N(Q_phi, n_phi)
        
        if name == 'mu': # Equation 35.
            mu = value
            MU = calcMU(mu)
            V = MU.inverse().times(N_lab).times(N_phi.inverse()).array
            phi = atan2(V[2][1], V[2][0])
            eta = atan2(-V[1][2], V[0][2])
            if self.choose_chi_from_0_to_pi:
                chi = acos(V[2][2]) # 0 < chi < pi
            else:
                chi = atan2(sqrt(V[2][0]**2+V[2][1]**2), V[2][2]) # -pi/2<chi< pi/2
                
        elif name == 'phi': # Equation 37
            phi = value
            PHI = calcPHI(phi)
            V = N_lab.times(N_phi.inverse()).times(PHI.inverse()).array
            eta = atan2(V[0][1], sqrt(V[1][1]**2+V[2][1]**2))
            mu = atan2(V[2][1], V[1][1])
            if self.choose_chi_from_0_to_pi:
                try:
                    chi = acos(V[0][0] / cos(eta)) # 0 < chi < pi
                except ZeroDivisionError:
                    raise ZeroDivisionError(
                           "Could not calculate chi given phi as cos(eta) is 0")
            else:
                chi = atan2(V[0][2], V[0][0]) # -pi/2 < chi < pi/2
                
        elif name in ('eta', 'chi'):
            V = N_lab.times(N_phi.inverse()).array
            if name == 'eta': # Equation 39
                eta = value
                if self.choose_chi_from_0_to_pi:
                    raise DiffcalcException(
"""A chi value from 0 to pi was requested, but with eta constrained, this is not
currently possible. (Set the choose_chi_from_0_to_pi attribute on the
YouHklCalculator object to False to relax this requirement.)""")
                if is_small(eta):
                    raise ValueError(
"Chi and mu cannot be chosen uniquely with eta so close to +-90.")
                try:
                    chi = asin(V[0][2] / cos(eta)) # -pi/2 < chi < pi/2
                except ZeroDivisionError:
                    raise ZeroDivisionError(
                           "Could not calculate chi given eta as cos(eta) is 0")

            else: # name == 'chi', Equation 40
                chi = value
                if chi < 0 or chi > pi: # TODO: what if equal
                    print (
"""WARNING: when calculating eta given chi, chi is outside the range 0 to pi
specified in equation 40.""")
                if is_small(chi):
                    raise ValueError(
"Eta and phi cannot be chosen uniquely with chi constrained so close to 0.")
                eta = acos(V[0][2] / sin(chi))
            # Equation 41:
            # The atan2 function chooses the wrong sign. At least for:
            # test_calcvlieg.test_constrain_eta_0_wasfailing. The atan2 function
            # could be used (in this case) if the sign of top and bottom were
            # flipped.
            top = V[2][2]*sin(eta)*sin(chi) + V[1][2]*cos(chi)
            bottom = -V[2][2]*cos(chi) + V[1][2]*sin(eta)*sin(chi)
            if is_small(bottom):
                mu = 0 if is_small(top) else sign(top) * sign(bottom) * pi/2
            else:
                mu = atan(top / bottom)
            
            #Equation 42:
            phi = atan2(V[0][1]*cos(eta)*cos(chi) - V[0][0]*sin(eta),
                      V[0][1]*sin(eta) + V[0][0]*cos(eta)*cos(chi))
                
        else:
            raise ValueError('Given angle must be one of phi, chi, eta or mu')
            
        return phi, chi, eta, mu
                
                
    

        