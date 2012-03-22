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

from math import pi, asin, acos, sin, cos, sqrt, atan2, fabs, atan

try:
    from numpy import matrix
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix
    from numjy.linalg import norm

from diffcalc.hkl.calcbase import HklCalculatorBase
from diffcalc.hkl.vlieg.transform import TransformCInRadians
from diffcalc.util import dot3, cross3, bound, differ
from diffcalc.hkl.vlieg.geometry import createVliegMatrices, \
    createVliegsPsiTransformationMatrix, \
    createVliegsSurfaceTransformationMatrices, calcPHI
from diffcalc.hkl.vlieg.geometry import VliegPosition
from diffcalc.hkl.vlieg.constraints import VliegParameterManager
from diffcalc.hkl.vlieg.constraints import ModeSelector
from diffcalc.ub.calc import PaperSpecificUbCalcStrategy


TORAD = pi / 180
TODEG = 180 / pi
transformC = TransformCInRadians()


PREFER_POSITIVE_CHI_SOLUTIONS = True

I = matrix('1 0 0; 0 1 0; 0 0 1')
y = matrix('0; 1; 0')


def check(condition, ErrorOrStringOrCallable, *args):
    """
    fail = check(condition, ErrorOrString) -- if condition is false raises the
    Exception passed in, or creates one from a string. If a callable function
    is passed in this is called with any args specified and the thing returns
    false.
    """
    # TODO: Remove (really nasty) check function
    if condition == False:
        if callable(ErrorOrStringOrCallable):
            ErrorOrStringOrCallable(*args)
            return False
        elif isinstance(ErrorOrStringOrCallable, str):
            raise Exception(ErrorOrStringOrCallable)
        else:  # assume input is an exception
            raise ErrorOrStringOrCallable
    return True


def sign(x):
    if x < 0:
        return -1
    else:
        return 1


def vliegAnglesToHkl(pos, wavelength, UBMatrix):
    """
    Returns hkl indices from pos object in radians.
    """
    wavevector = 2 * pi / wavelength

    # Create transformation matrices
    [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
        pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)

    # Create the plane normal vector in the alpha axis coordinate frame
    qa = ((DELTA * GAMMA) - ALPHA.I) * matrix([[0], [wavevector], [0]])

    # Transform the plane normal vector from the alpha frame to reciprical
    # lattice frame.
    hkl = UBMatrix.I * PHI.I * CHI.I * OMEGA.I * qa

    return hkl[0, 0], hkl[1, 0], hkl[2, 0]


class VliegUbCalcStrategy(PaperSpecificUbCalcStrategy):

    def calculate_q_phi(self, pos):

        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
           pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)

        u1a = (DELTA * GAMMA - ALPHA.I) * y
        u1p = PHI.I * CHI.I * OMEGA.I * u1a
        return u1p


class VliegHklCalculator(HklCalculatorBase):

    def __init__(self, ubcalc, geometry, hardware,
                 raiseExceptionsIfAnglesDoNotMapBackToHkl=True):
        r = raiseExceptionsIfAnglesDoNotMapBackToHkl
        HklCalculatorBase.__init__(self, ubcalc, geometry, hardware,
                                   raiseExceptionsIfAnglesDoNotMapBackToHkl=r)
        self._gammaParameterName = ({'arm': 'gamma', 'base': 'oopgamma'}
                                    [self._geometry.gamma_location])
        self.mode_selector = ModeSelector(self._geometry, None,
                                          self._gammaParameterName)
        self.parameter_manager = VliegParameterManager(
            self._geometry, self._hardware, self.mode_selector,
            self._gammaParameterName)
        self.mode_selector.setParameterManager(self.parameter_manager)

    def __str__(self):
        # should list paramemeters and indicate which are used in selected mode
        result = "Available mode_selector:\n"
        result += self.mode_selector.reportAvailableModes()
        result += '\nCurrent mode:\n'
        result += self.mode_selector.reportCurrentMode()
        result += '\n\nParameters:\n'
        result += self.parameter_manager.reportAllParameters()
        return result

    def _anglesToHkl(self, pos, wavelength):
        """
        Return hkl tuple from VliegPosition in radians and wavelength in
        Angstroms.
        """
        return vliegAnglesToHkl(pos, wavelength, self._getUBMatrix())

    def _anglesToVirtualAngles(self, pos, wavelength):
        """
        Return dictionary of all virtual angles in radians from VliegPosition
        object win radians and wavelength in Angstroms. The virtual angles are:
        Bin, Bout, azimuth and 2theta.
        """

        # Create transformation matrices
        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
            pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)
        [SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(
            self._getSigma() * TORAD, self._getTau() * TORAD)

        S = TAU * SIGMA
        y_vector = matrix([[0], [1], [0]])

        # Calculate Bin from equation 15:
        surfacenormal_alpha = OMEGA * CHI * PHI * S * matrix([[0], [0], [1]])
        incoming_alpha = ALPHA.I * y_vector
        minusSinBetaIn = dot3(surfacenormal_alpha, incoming_alpha)
        Bin = asin(bound(-minusSinBetaIn))

        # Calculate Bout from equation 16:
        #  surfacenormal_alpha has just ben calculated
        outgoing_alpha = DELTA * GAMMA * y_vector
        sinBetaOut = dot3(surfacenormal_alpha, outgoing_alpha)
        Bout = asin(bound(sinBetaOut))

        # Calculate 2theta from equation 25:

        cosTwoTheta = dot3(ALPHA * DELTA * GAMMA * y_vector, y_vector)
        twotheta = acos(bound(cosTwoTheta))
        psi = self._anglesToPsi(pos, wavelength)

        return {'Bin': Bin, 'Bout': Bout, 'azimuth': psi, '2theta': twotheta}

    def _hklToAngles(self, h, k, l, wavelength):
        """
        Return VliegPosition and virtual angles in radians from h, k & l and
        wavelength in Angstroms. The virtual angles are those fixed or
        generated while calculating the position: Bin, Bout and 2theta; and
        azimuth in four and five circle modes.
        """

        if self._getMode().group in ("fourc", "fivecFixedGamma",
                                     "fivecFixedAlpha"):
            return self._hklToAnglesFourAndFiveCirclesModes(h, k, l,
                                                            wavelength)
        elif self._getMode().group == "zaxis":
            return self._hklToAnglesZaxisModes(h, k, l, wavelength)
        else:
            raise RuntimeError(
                'The current mode (%s) has an unrecognised group: %s.'
                 % (self._getMode().name, self._getMode().group))

    def _hklToAnglesFourAndFiveCirclesModes(self, h, k, l, wavelength):
        """
        Return VliegPosition and virtual angles in radians from h, k & l and
        wavelength in Angstrom for four and five circle modes. The virtual
        angles are those fixed or generated while calculating the position:
        Bin, Bout, 2theta and azimuth.
        """

        # Results in radians during calculations, returned in degreess
        pos = VliegPosition(None, None, None, None, None, None)

        # Normalise hkl
        wavevector = 2 * pi / wavelength
        hklNorm = matrix([[h], [k], [l]]) / wavevector

        # Compute hkl in phi axis coordinate frame
        hklPhiNorm = self._getUBMatrix() * hklNorm

        # Determine Bin and Bout
        if self._getMode().name == '4cPhi':
            Bin = Bout = None
        else:
            Bin, Bout = self._determineBinAndBoutInFourAndFiveCirclesModes(
                                                                    hklNorm)

        # Determine alpha and gamma
        if self._getMode().group == 'fourc':
            pos.alpha, pos.gamma = \
                self._determineAlphaAndGammaForFourCircleModes(hklPhiNorm)
        else:
            pos.alpha, pos.gamma = \
                self._determineAlphaAndGammaForFiveCircleModes(Bin, hklPhiNorm)
        if pos.alpha < -pi:
            pos.alpha += 2 * pi
        if pos.alpha > pi:
            pos.alpha -= 2 * pi

        # Determine delta
        (pos.delta, twotheta) = self._determineDelta(hklPhiNorm, pos.alpha,
                                                     pos.gamma)

        # Determine omega, chi & phi
        pos.omega, pos.chi, pos.phi, psi = \
            self._determineSampleAnglesInFourAndFiveCircleModes(
                hklPhiNorm, pos.alpha, pos.delta, pos.gamma, Bin)
        # (psi will be None in fixed phi mode)

        # Ensure that by default omega is between -90 and 90, by possibly
        # transforming the sample angles
        if self._getMode().name != '4cPhi':  # not in fixed-phi mode
            if pos.omega < -pi / 2 or pos.omega > pi / 2:
                pos = transformC.transform(pos)

        # Gather up the virtual angles calculated along the way...
        #   -pi<psi<=pi
        if psi is not None:
            if psi > pi:
                psi -= 2 * pi
            if psi < (-1 * pi):
                psi += 2 * pi

        v = {'2theta': twotheta, 'Bin': Bin, 'Bout': Bout, 'azimuth': psi}
        return pos, v

    def _hklToAnglesZaxisModes(self, h, k, l, wavelength):
        """
        Return VliegPosition and virtual angles in radians from h, k & l and
        wavelength in Angstroms for z-axis modes. The virtual angles are those
        fixed or generated while calculating the position: Bin, Bout, and
        2theta.
        """
        # Section 6:

        # Results in radians during calculations, returned in degreess
        pos = VliegPosition(None, None, None, None, None, None)

        # Normalise hkl
        wavevector = 2 * pi / wavelength
        hkl = matrix([[h], [k], [l]])
        hklNorm = hkl * (1.0 / wavevector)

        # Compute hkl in phi axis coordinate frame
        hklPhi = self._getUBMatrix() * hkl
        hklPhiNorm = self._getUBMatrix() * hklNorm

        # Determine Chi and Phi (Equation 29):
        pos.phi = -self._getTau() * TORAD
        pos.chi = -self._getSigma() * TORAD

        # Equation 30:
        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
                None, None, None, None, pos.chi, pos.phi)
        del ALPHA, DELTA, GAMMA, OMEGA
        Hw = CHI * PHI * hklPhi

        # Determine Bin and Bout:
        (Bin, Bout) = self._determineBinAndBoutInZaxisModes(
            Hw[2, 0] / wavevector)

        # Determine Alpha and Gamma (Equation 32):
        pos.alpha = Bin
        pos.gamma = Bout

        # Determine Delta:
        (pos.delta, twotheta) = self._determineDelta(hklPhiNorm, pos.alpha,
                                                     pos.gamma)

        # Determine Omega:
        delta = pos.delta
        gamma = pos.gamma
        d1 = (Hw[1, 0] * sin(delta) * cos(gamma) - Hw[0, 0] *
              (cos(delta) * cos(gamma) - cos(pos.alpha)))
        d2 = (Hw[0, 0] * sin(delta) * cos(gamma) + Hw[1, 0] *
              (cos(delta) * cos(gamma) - cos(pos.alpha)))

        if fabs(d2) < 1e-30:
            pos.omega = sign(d1) * sign(d2) * pi / 2.0
        else:
            pos.omega = atan2(d1, d2)

        # Gather up the virtual angles calculated along the way
        return pos, {'2theta': twotheta, 'Bin': Bin, 'Bout': Bout}

###

    def _determineBinAndBoutInFourAndFiveCirclesModes(self, hklNorm):
        """(Bin, Bout) = _determineBinAndBoutInFourAndFiveCirclesModes()"""
        BinModes = ('4cBin', '5cgBin', '5caBin')
        BoutModes = ('4cBout', '5cgBout', '5caBout')
        BeqModes = ('4cBeq', '5cgBeq', '5caBeq')
        azimuthModes = ('4cAzimuth')
        fixedBusingAndLeviWmodes = ('4cFixedw')

        # Calculate RHS of equation 20
        # RHS (1/K)(S^-1*U*B*H)_3 where H/K = hklNorm
        UB = self._getUBMatrix()
        [SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(
            self._getSigma() * TORAD, self._getTau() * TORAD)
        #S = SIGMA * TAU
        S = TAU * SIGMA
        RHS = (S.I * UB * hklNorm)[2, 0]

        if self._getMode().name in BinModes:
            Bin = self._getParameter('betain')
            check(Bin != None, "The parameter betain must be set for mode %s" %
                  self._getMode().name)
            Bin = Bin * TORAD
            sinBout = RHS - sin(Bin)
            check(fabs(sinBout) <= 1, "Could not compute Bout")
            Bout = asin(sinBout)

        elif self._getMode().name in BoutModes:
            Bout = self._getParameter('betaout')
            check(Bout != None, "The parameter Bout must be set for mode %s" %
                  self._getMode().name)
            Bout = Bout * TORAD
            sinBin = RHS - sin(Bout)
            check(fabs(sinBin) <= 1, "Could not compute Bin")
            Bin = asin(sinBin)

        elif self._getMode().name in BeqModes:
            sinBeq = RHS / 2
            check(fabs(sinBeq) <= 1, "Could not compute Bin=Bout")
            Bin = Bout = asin(sinBeq)

        elif self._getMode().name in azimuthModes:
            azimuth = self._getParameter('azimuth')
            check(azimuth != None, "The parameter azimuth must be set for "
                  "mode %s" % self._getMode().name)
            del azimuth
            # TODO: codeit
            raise NotImplementedError()

        elif self._getMode().name in fixedBusingAndLeviWmodes:
            bandlomega = self._getParameter('blw')
            check(bandlomega != None, "The parameter abandlomega must be set "
                  "for mode %s" % self._getMode().name)
            del bandlomega
            # TODO: codeit
            raise NotImplementedError()
        else:
            raise RuntimeError("AngleCalculator does not know how to handle "
                               "mode %s" % self._getMode().name)

        return (Bin, Bout)

    def _determineBinAndBoutInZaxisModes(self, Hw3OverK):
        """(Bin, Bout) = _determineBinAndBoutInZaxisModes(HwOverK)"""
        BinModes = ('6czBin')
        BoutModes = ('6czBout')
        BeqModes = ('6czBeq')

        if self._getMode().name in BinModes:
            Bin = self._getParameter('betain')
            check(Bin != None, "The parameter betain must be set for mode %s" %
                  self._getMode().name)
            Bin = Bin * TORAD
            # Equation 32a:
            Bout = asin(Hw3OverK - sin(Bin))

        elif self._getMode().name in BoutModes:
            Bout = self._getParameter('betaout')
            check(Bout != None, "The parameter Bout must be set for mode %s" %
                  self._getMode().name)
            Bout = Bout * TORAD
            # Equation 32b:
            Bin = asin(Hw3OverK - sin(Bout))

        elif self._getMode().name in BeqModes:
            # Equation 32c:
            Bin = Bout = asin(Hw3OverK / 2)

        return (Bin, Bout)

###

    def _determineAlphaAndGammaForFourCircleModes(self, hklPhiNorm):

        if self._getMode().group == 'fourc':
            alpha = self._getParameter('alpha') * TORAD
            gamma = self._getParameter(self._getGammaParameterName()) * TORAD
            check(alpha != None, "alpha parameter must be set in fourc modes")
            check(gamma != None, "gamma parameter must be set in fourc modes")
            return alpha, gamma
        else:
            raise RuntimeError(
                "determineAlphaAndGammaForFourCirclesModes() "
                "is not appropriate for %s modes" % self._getMode().group)

    def _determineAlphaAndGammaForFiveCircleModes(self, Bin, hklPhiNorm):

        ## Solve equation 34 for one possible Y, Yo
        # Calculate surface normal in phi frame
        [SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(
            self._getSigma() * TORAD, self._getTau() * TORAD)
        S = TAU * SIGMA
        surfaceNormalPhi = S * matrix([[0], [0], [1]])
        # Compute beta in vector
        BetaVector = matrix([[0], [-sin(Bin)], [cos(Bin)]])
        # Find Yo
        Yo = self._findMatrixToTransformAIntoB(surfaceNormalPhi, BetaVector)

        ## Calculate Hv from equation 39
        Z = matrix([[1, 0, 0],
                    [0, cos(Bin), sin(Bin)],
                    [0, -sin(Bin), cos(Bin)]])
        Hv = Z * Yo * hklPhiNorm
        # Fixed gamma:
        if self._getMode().group == 'fivecFixedGamma':
            gamma = self._getParameter(self._getGammaParameterName())
            check(gamma != None,
                  "gamma parameter must be set in fivecFixedGamma modes")
            gamma = gamma * TORAD
            H2 = (hklPhiNorm[0, 0] ** 2 + hklPhiNorm[1, 0] ** 2 +
                  hklPhiNorm[2, 0] ** 2)
            a = -(0.5 * H2 * sin(Bin) - Hv[2, 0])
            b = -(1.0 - 0.5 * H2) * cos(Bin)
            c = cos(Bin) * sin(gamma)
            check((b * b + a * a - c * c) >= 0, 'Could not solve for alpha')
            alpha = 2 * atan2(-(b + sqrt(b * b + a * a - c * c)), -(a + c))

        # Fixed Alpha:
        elif self._getMode().group == 'fivecFixedAlpha':
            alpha = self._getParameter('alpha')
            check(alpha != None,
                  "alpha parameter must be set in fivecFixedAlpha modes")
            alpha = alpha * TORAD
            H2 = (hklPhiNorm[0, 0] ** 2 + hklPhiNorm[1, 0] ** 2 +
                  hklPhiNorm[2, 0] ** 2)
            t0 = ((2 * cos(alpha) * Hv[2, 0] - sin(Bin) * cos(alpha) * H2 +
                  cos(Bin) * sin(alpha) * H2 - 2 * cos(Bin) * sin(alpha)) /
                  (cos(Bin) * 2.0))
            check(abs(t0) <= 1, "Cannot compute gamma: sin(gamma)>1")
            gamma = asin(t0)
        else:
            raise RuntimeError(
                "determineAlphaAndGammaInFiveCirclesModes() is not "
                "appropriate for %s modes" % self._getMode().group)

        return (alpha, gamma)

###

    def _determineDelta(self, hklPhiNorm, alpha, gamma):
        """
        (delta, twotheta) = _determineDelta(hklPhiNorm, alpha, gamma) --
        computes delta for all modes. Also returns twotheta for sanity
        checking. hklPhiNorm is a 3X1 matrix.

        alpha, gamma & delta - in radians.
        h k & l normalised to wavevector and in phi axis coordinates
        """
        h = hklPhiNorm[0, 0]
        k = hklPhiNorm[1, 0]
        l = hklPhiNorm[2, 0]
        # See Vlieg section 5 (with K=1)
        cosdelta = ((1 + sin(gamma) * sin(alpha) - (h * h + k * k + l * l) / 2)
                    / (cos(gamma) * cos(alpha)))
        costwotheta = (cos(alpha) * cos(gamma) * bound(cosdelta) -
                       sin(alpha) * sin(gamma))
        return (acos(bound(cosdelta)), acos(bound(costwotheta)))

    def _determineSampleAnglesInFourAndFiveCircleModes(self, hklPhiNorm, alpha,
                                                       delta, gamma, Bin):
        """
        (omega, chi, phi, psi)=determineNonZAxisSampleAngles(hklPhiNorm, alpha,
        delta, gamma, sigma, tau) where hkl has been normalised by the
        wavevector and is in the phi Axis coordinate frame. All angles in
        radians. hklPhiNorm is a 3X1 matrix
        """

        def equation49through59(psi):
            # equation 49 R = (D^-1)*PI*D*Ro
            PSI = createVliegsPsiTransformationMatrix(psi)
            R = D.I * PSI * D * Ro

            #  eq 57: extract omega from R
            if abs(R[0, 2]) < 1e-20:
                omega = -sign(R[1, 2]) * sign(R[0, 2]) * pi / 2
            else:
                omega = -atan2(R[1, 2], R[0, 2])

            # eq 58: extract chi from R
            sinchi = sqrt(pow(R[0, 2], 2) + pow(R[1, 2], 2))
            sinchi = bound(sinchi)
            check(abs(sinchi) <= 1, 'could not compute chi')
            # (there are two roots to this equation, but only the first is also
            # a solution to R33=cos(chi))
            chi = asin(sinchi)

            # eq 59: extract phi from R
            if abs(R[2, 0]) < 1e-20:
                phi = sign(R[2, 1]) * sign(R[2, 1]) * pi / 2
            else:
                phi = atan2(-R[2, 1], -R[2, 0])
            return omega, chi, phi

        def checkSolution(omega, chi, phi):
            _, _, _, OMEGA, CHI, PHI = createVliegMatrices(
                None, None, None, omega, chi, phi)
            R = OMEGA * CHI * PHI
            RtimesH_phi = R * H_phi
            print ("R*H_phi=%s, Q_alpha=%s" %
                   (R * H_phi.tolist(), Q_alpha.tolist()))
            return not differ(RtimesH_phi, Q_alpha, .0001)

        # Using Vlieg section 7.2

        # Needed througout:
        [ALPHA, DELTA, GAMMA, _, _, _] = createVliegMatrices(
            alpha, delta, gamma, None, None, None)

        ## Find Ro, one possible solution to equation 46: R*H_phi=Q_alpha

        # Normalise hklPhiNorm (As it is currently normalised only to the
        # wavevector)
        normh = norm(hklPhiNorm)
        check(normh >= 1e-10, "reciprical lattice vector too close to zero")
        H_phi = hklPhiNorm * (1 / normh)

        # Create Q_alpha from equation 47, (it comes normalised)
        Q_alpha = ((DELTA * GAMMA) - ALPHA.I) * matrix([[0], [1], [0]])
        Q_alpha = Q_alpha * (1 / norm(Q_alpha))

        if self._getMode().name == '4cPhi':
            ### Use the fixed value of phi as the final constraint ###
            phi = self._getParameter('phi') * TORAD
            PHI = calcPHI(phi)
            H_chi = PHI * H_phi
            omega, chi = _findOmegaAndChiToRotateHchiIntoQalpha(H_chi, Q_alpha)
            return (omega, chi, phi, None)  # psi = None as not calculated
        else:
            ### Use Bin as the final constraint ###

            # Find a solution Ro to Ro*H_phi=Q_alpha
            Ro = self._findMatrixToTransformAIntoB(H_phi, Q_alpha)

            ## equation 50: Find a solution D to D*Q=norm(Q)*[[1],[0],[0]])
            D = self._findMatrixToTransformAIntoB(
                Q_alpha, matrix([[1], [0], [0]]))

            ## Find psi and create PSI

            # eq 54: compute u=D*Ro*S*[[0],[0],[1]], the surface normal in
            # psi frame
            [SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(
                self._getSigma() * TORAD, self._getTau() * TORAD)
            S = TAU * SIGMA
            [u1], [u2], [u3] = (D * Ro * S * matrix([[0], [0], [1]])).tolist()
            # TODO: If u points along 100, then any psi is a solution. Choose 0
            if not differ([u1, u2, u3], [1, 0, 0], 1e-9):
                psi = 0
                omega, chi, phi = equation49through59(psi)
            else:
                # equation 53: V=A*(D^-1)
                V = ALPHA * D.I
                v21 = V[1, 0]
                v22 = V[1, 1]
                v23 = V[1, 2]
                # equation 55
                a = v22 * u2 + v23 * u3
                b = v22 * u3 - v23 * u2
                c = -sin(Bin) - v21 * u1  # TODO: changed sign from paper

                # equation 44
                # Try first root:
                def myatan2(y, x):
                    if abs(x) < 1e-20 and abs(y) < 1e-20:
                        return pi / 2
                    else:
                        return atan2(y, x)
                psi = 2 * myatan2(-(b - sqrt(b * b + a * a - c * c)), -(a + c))
                #psi = -acos(c/sqrt(a*a+b*b))+atan2(b,a)# -2*pi
                omega, chi, phi = equation49through59(psi)

            # if u points along z axis, the psi could have been either 0 or 180
            if (not differ([u1, u2, u3], [0, 0, 1], 1e-9) and
                abs(psi - pi) < 1e-10):
                # Choose 0 to match that read up by  angles-to-virtual-angles
                psi = 0.
            # if u points a long
            return (omega, chi, phi, psi)

    def _anglesToPsi(self, pos, wavelength):
        """
        pos assumed in radians. -180<= psi <= 180
        """
        # Using Vlieg section 7.2

        # Needed througout:
        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
                pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)

        # Solve equation 49 for psi, the rotation of the a reference solution
        # about Qalpha or H_phi##

        # Find Ro, the reference solution to equation 46: R*H_phi=Q_alpha

        # Create Q_alpha from equation 47, (it comes normalised)
        Q_alpha = ((DELTA * GAMMA) - ALPHA.I) * matrix([[0], [1], [0]])
        Q_alpha = Q_alpha * (1 / norm(Q_alpha))

        # Finh H_phi
        h, k, l = self._anglesToHkl(pos, wavelength)
        H_phi = self._getUBMatrix() * matrix([[h], [k], [l]])
        normh = norm(H_phi)
        check(normh >= 1e-10, "reciprical lattice vector too close to zero")
        H_phi = H_phi * (1 / normh)

        # Find a solution Ro to Ro*H_phi=Q_alpha
        # This the reference solution with zero azimuth (psi)
        Ro = self._findMatrixToTransformAIntoB(H_phi, Q_alpha)

        # equation 48:
        R = OMEGA * CHI * PHI

        ## equation 50: Find a solution D to D*Q=norm(Q)*[[1],[0],[0]])
        D = self._findMatrixToTransformAIntoB(Q_alpha, matrix([[1], [0], [0]]))

        # solve equation 49 for psi
        # D*R = PSI*D*Ro
        # D*R*(D*Ro)^-1 = PSI
        PSI = D * R * ((D * Ro).I)

        # Find psi within PSI as defined in equation 51
        PSI_23 = PSI[1, 2]
        PSI_33 = PSI[2, 2]
        psi = atan2(PSI_23, PSI_33)

        #print "PSI: ", PSI.tolist()
        return psi

    def _findMatrixToTransformAIntoB(self, a, b):
        """
        Finds a particular matrix Mo that transforms the unit vector a into the
        unit vector b. Thats is it finds Mo Mo*a=b. a and b 3x1 matrixes and Mo
        is a 3x3 matrix.

        Throws an exception if this is not possible.
            """
        # Maths from the appendix of "Angle caluculations
        # for a 5-circle diffractometer used for surface X-ray diffraction",
        # E. Vlieg, J.F. van der Veen, J.E. Macdonald and M. Miller, J. of
        # Applied Cryst. 20 (1987) 330.
        #                                       - courtesy of Elias Vlieg again

        # equation A2: compute angle xi between vectors a and b
        cosxi = dot3(a, b)
        try:
            cosxi = bound(cosxi)
        except ValueError:
            raise Exception("Could not compute cos(xi), vectors a=%f and b=%f "
                            "must be of unit length" % (norm(a), norm(b)))
        xi = acos(cosxi)

        # Mo is identity matrix if xi zero (math below would blow up)
        if abs(xi) < 1e-10:
            return I

        # equation A3: c=cross(a,b)/sin(xi)
        c = cross3(a, b) * (1 / sin(xi))

        # equation A4: find D matrix that transforms a into the frame
        # x = a; y = c x a; z = c. */
        a1 = a[0, 0]
        a2 = a[1, 0]
        a3 = a[2, 0]
        c1 = c[0, 0]
        c2 = c[1, 0]
        c3 = c[2, 0]
        D = matrix([[a1, a2, a3],
                    [c2 * a3 - c3 * a2, c3 * a1 - c1 * a3, c1 * a2 - c2 * a1],
                    [c1, c2, c3]])

        # equation A5: create Xi to rotate by xi about z-axis
        XI = matrix([[cos(xi), -sin(xi), 0],
                     [sin(xi), cos(xi), 0],
                     [0, 0, 1]])

        # eq A6: compute Mo
        return D.I * XI * D


def _findOmegaAndChiToRotateHchiIntoQalpha(h_chi, q_alpha):
    """
    (omega, chi) = _findOmegaAndChiToRotateHchiIntoQalpha(H_chi, Q_alpha)

    Solves for omega and chi in OMEGA*CHI*h_chi = q_alpha where h_chi and
    q_alpha are 3x1 matrices with unit length. Omega and chi are returned in
    radians.

    Throws an exception if this is not possible.
    """

    def solve(a, b, c):
        """
        x1,x2 =  solve(a , b, c)
        solves for the two solutions to x in equations of the form
            a*sin(x) + b*cos(x) = c
        by using the trigonometric identity
            a*sin(x) + b*cos(x) = a*sin(x)+b*cos(x)=sqrt(a**2+b**2)-sin(x+p)
        where
            p = atan(b/a) + {0 if a>=0
                            {pi if a<0
        """
        if a == 0:
            p = pi / 2 if b >= 0 else - pi / 2
        else:
            p = atan(b / a)
        if a < 0:
            p = p + pi
        guts = c / sqrt(a ** 2 + b ** 2)
        if guts < -1:
            guts = -1
        elif guts > 1:
            guts = 1
        left1 = asin(guts)
        left2 = pi - left1
        return (left1 - p, left2 - p)

    def ne(a, b):
        """
        shifts a and b in between -pi and pi and tests for near equality
        """
        def shift(a):
            if a > pi:
                return a - 2 * pi
            elif a <= -pi:
                return a + 2 * pi
            else:
                return a
        return abs(shift(a) - shift(b)) < .0000001

    # 1. Compute some solutions
    h_chi1 = h_chi[0, 0]
    h_chi2 = h_chi[1, 0]
    h_chi3 = h_chi[2, 0]
    q_alpha1 = q_alpha[0, 0]
    q_alpha2 = q_alpha[1, 0]
    q_alpha3 = q_alpha[2, 0]

    try:
        # a) Solve for chi using Equation 3
        chi1, chi2 = solve(-h_chi1, h_chi3, q_alpha3)

        # b) Solve for omega Equation 1 and each chi
        B = h_chi1 * cos(chi1) + h_chi3 * sin(chi1)
        eq1omega11, eq1omega12 = solve(h_chi2, B, q_alpha1)
        B = h_chi1 * cos(chi2) + h_chi3 * sin(chi2)
        eq1omega21, eq1omega22 = solve(h_chi2, B, q_alpha1)

        # c) Solve for omega Equation 2 and each chi
        A = -h_chi1 * cos(chi1) - h_chi3 * sin(chi1)
        eq2omega11, eq2omega12 = solve(A, h_chi2, q_alpha2)
        A = -h_chi1 * cos(chi2) - h_chi3 * sin(chi2)
        eq2omega21, eq2omega22 = solve(A, h_chi2, q_alpha2)

    except ValueError, e:
        raise ValueError(
            str(e) + ":\nProblem in fixed-phi calculation for:\nh_chi: " +
            str(h_chi.tolist()) + " q_alpha: " + str(q_alpha.tolist()))

    # 2. Choose values of chi and omega that are solutions to equations 1 and 2
    solutions = []
    # a) Check the chi1 solutions
    print "_findOmegaAndChiToRotateHchiIntoQalpha:"
    if ne(eq1omega11, eq2omega11) or ne(eq1omega11, eq2omega12):
#        print "1: eq1omega11, chi1 = ", eq1omega11, chi1
        solutions.append((eq1omega11, chi1))
    if ne(eq1omega12, eq2omega11) or ne(eq1omega12, eq2omega12):
#        print "2: eq1omega12, chi1 = ", eq1omega12, chi1
        solutions.append((eq1omega12, chi1))
    # b) Check the chi2 solutions
    if ne(eq1omega21, eq2omega21) or ne(eq1omega21, eq2omega22):
#        print "3: eq1omega21, chi2 = ", eq1omega21, chi2
        solutions.append((eq1omega21, chi2))
    if ne(eq1omega22, eq2omega21) or ne(eq1omega22, eq2omega22):
#        print "4: eq1omega22, chi2 = ", eq1omega22, chi2
        solutions.append((eq1omega22, chi2))
#    print solutions
#    print "*"

    if len(solutions) == 0:
        e = "h_chi: " + str(h_chi.tolist())
        e += " q_alpha: " + str(q_alpha.tolist())
        e += ("\nchi1:%4f eq1omega11:%4f eq1omega12:%4f eq2omega11:%4f "
              "eq2omega12:%4f" % (chi1 * TODEG, eq1omega11 * TODEG,
              eq1omega12 * TODEG, eq2omega11 * TODEG, eq2omega12 * TODEG))
        e += ("\nchi2:%4f eq1omega21:%4f eq1omega22:%4f eq2omega21:%4f "
              "eq2omega22:%4f" % (chi2 * TODEG, eq1omega21 * TODEG,
              eq1omega22 * TODEG, eq2omega21 * TODEG, eq2omega22 * TODEG))
        raise Exception("Could not find simultaneous solution for this fixed "
                        "phi mode problem\n" + e)

    if not PREFER_POSITIVE_CHI_SOLUTIONS:
        return solutions[0]

    positive_chi_solutions = [sol for sol in solutions if sol[1] > 0]

    if len(positive_chi_solutions) == 0:
        print "WARNING: A +ve chi solution was requested, but none were found."
        print "         Returning a -ve one. Try the mapper"
        return solutions[0]

    if len(positive_chi_solutions) > 1:
        print ("INFO: Multiple +ve chi solutions were found [(omega, chi) ...]"
             " = " + str(positive_chi_solutions))
        print "      Returning the first"

    return positive_chi_solutions[0]
