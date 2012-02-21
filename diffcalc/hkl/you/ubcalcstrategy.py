from diffcalc.ub.calculation import PaperSpecificUbCalcStrategy
from diffcalc.hkl.you.matrices import createYouMatrices
try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

I = matrix('1 0 0; 0 1 0; 0 0 1')
y = matrix('0; 1; 0')

class YouUbCalcStrategy(PaperSpecificUbCalcStrategy):
    
    def calculate_q_phi(self, pos):
        
        [MU, DELTA, NU, ETA, CHI, PHI] = createYouMatrices(*pos.totuple())
        # Equation 12: Compute the momentum transfer vector in the lab  frame
        q_lab = (NU * DELTA - I) * y
        # Transform this into the phi frame. 
        return PHI.I * CHI.I * ETA.I * MU.I * q_lab 
