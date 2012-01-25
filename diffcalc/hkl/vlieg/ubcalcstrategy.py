from diffcalc.ub.calculation import PaperSpecificUbCalcStrategy
from diffcalc.hkl.vlieg.matrices import createVliegMatrices
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

I = Matrix.identity(3, 3)

class VliegUbCalcStrategy(PaperSpecificUbCalcStrategy):
    
    def calculate_q_phi(self, pos):
        
        [ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI] = createVliegMatrices(
           pos.alpha, pos.delta, pos.gamma, pos.omega, pos.chi, pos.phi)
        
        u1a = ((DELTA.times(GAMMA)).minus(ALPHA.inverse())).times(Matrix([[0], [1], [0]]))
        u1p = (PHI.inverse()).times(CHI.inverse()).times(OMEGA.inverse()).times(u1a)
        return u1p