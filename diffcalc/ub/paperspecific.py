try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
from diffcalc.utils import createVliegMatrices, createYouMatrices

I = Matrix.identity(3, 3)


class PaperSpecificUbCalcStrategy(object):   
    pass 
    
    
class VliegUbCalcStrategy(PaperSpecificUbCalcStrategy):
    
    def calculateObserveredPlaneNormalInPhiFrame(self, pos):
        
        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
           pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)
        
        u1a = ((DELTA.times(GAMMA)).minus(ALPHA.inverse())).times(Matrix([[0], [1], [0]]))
        u1p = (PHI.inverse()).times(CHI.inverse()).times(OMEGA.inverse()).times(u1a)
        return u1p

    
class YouUbCalcStrategy(PaperSpecificUbCalcStrategy):
    
    def calculateObserveredPlaneNormalInPhiFrame(self, pos):
        
        [MU, DELTA, NU, ETA, CHI, PHI] = createYouMatrices(*pos.totuple())
        # Equation 12: Compute the momentum transfer vector in the lab  frame
        q_lab = ((NU.times(DELTA)).minus(I)).times(Matrix([[0], [1], [0]]))
        # Transform this into the phi frame. 
        return PHI.inverse().times(CHI.inverse()).times(ETA.inverse()).times(MU.inverse()).times(q_lab)

        
    
