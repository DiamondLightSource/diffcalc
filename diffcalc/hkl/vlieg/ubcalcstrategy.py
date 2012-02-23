try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.ub.calculation import PaperSpecificUbCalcStrategy
from diffcalc.hkl.vlieg.matrices import createVliegMatrices

I = matrix('1 0 0; 0 1 0; 0 0 1')
y = matrix('0; 1; 0')


class VliegUbCalcStrategy(PaperSpecificUbCalcStrategy):

    def calculate_q_phi(self, pos):

        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
           pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)

        u1a = (DELTA * GAMMA - ALPHA.I) * y
        u1p = PHI.I * CHI.I * OMEGA.I * u1a
        return u1p
