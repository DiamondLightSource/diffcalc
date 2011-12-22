from diffcalc.utils import Position
from diffcalc.tools import arrayeq_
from diffcalc.hkl.you.calcyou import youAnglesToHkl
from math import pi

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

TORAD = pi / 180
TODEG = 180 / pi



I = Matrix.identity(3, 3)


def posFromI16sEuler(phi, chi, eta, mu, delta, gamma):
    return Position(mu, delta, gamma, eta, chi, phi)

class TestAnglesToHkl_I16Examples():
    
    def __init__(self):
        self.UB1 = Matrix(
             ((0.9996954135095477, -0.01745240643728364, -0.017449748351250637),
              (0.01744974835125045, 0.9998476951563913, -0.0003045864904520898),
              (0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912))
            ).times(2 * pi)
        self.WL1 = 1 # Angstrom

    def test_anglesToHkl_mu_0_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1, 0, 0])
    
    def test_anglesToHkl_mu_0_gam_10(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 10).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1.00379806, -0.006578435, 0.08682408])
        
    def test_anglesToHkl_mu_10_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 10, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [0.99620193, 0.0065784359, 0.08682408])
        
    def test_anglesToHkl_arbitrary(self):
        pos = posFromI16sEuler(1.9, 2.9, 30.9, 0.9, 60.9, 2.9).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1.01174189, 0.02368622, 0.06627361])