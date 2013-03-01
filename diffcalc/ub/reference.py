from math import pi

try:
    from numpy import matrix, hstack
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix, hstack
    from numjy.linalg import norm

SMALL = 1e-7
TODEG = 180 / pi


class YouReference:
    
    def __init__(self, ubcalc):
        self._ubcalc = ubcalc
        self.n_phi = matrix([[0], [0], [1]])