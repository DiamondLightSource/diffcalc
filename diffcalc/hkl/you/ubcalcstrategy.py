from diffcalc.ub.calculation import PaperSpecificUbCalcStrategy
from diffcalc.hkl.you.matrices import createYouMatrices
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

I = Matrix.identity(3, 3)

class YouUbCalcStrategy(PaperSpecificUbCalcStrategy):
    
    def calculate_q_phi(self, pos):
        
        [MU, DELTA, NU, ETA, CHI, PHI] = createYouMatrices(*pos.totuple())
        # Equation 12: Compute the momentum transfer vector in the lab  frame
        q_lab = ((NU.times(DELTA)).minus(I)).times(Matrix([[0], [1], [0]]))
        # Transform this into the phi frame. 
        return PHI.inverse().times(CHI.inverse()).times(ETA.inverse()).times(MU.inverse()).times(q_lab)
