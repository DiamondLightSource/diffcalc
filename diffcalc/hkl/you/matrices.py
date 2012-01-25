from diffcalc.utils import x_rotation, z_rotation, y_rotation
def createYouMatrices(mu=None, delta=None, nu=None, eta=None, chi=None, phi=None):
    """    
    Return transformation matrices from H. You's paper.
    """    
    MU = None if mu is None else calcMU(mu)
    DELTA = None if delta is None else calcDELTA(delta)
    NU = None if nu is None else calcNU(nu)
    ETA = None if eta is None else calcETA(eta)
    CHI = None if chi is None else calcCHI(chi)
    PHI = None if phi is None else calcPHI(phi)
    return MU, DELTA, NU, ETA, CHI, PHI


def calcNU(nu):
    return x_rotation(nu)

def calcDELTA(delta):
    return z_rotation(-delta)

def calcMU(mu_or_alpha):
    return x_rotation(mu_or_alpha)

def calcETA(eta):
    return z_rotation(-eta)

def calcCHI(chi):
    return y_rotation(chi)

def calcPHI(phi):
    return z_rotation(-phi)
