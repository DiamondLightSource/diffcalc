from math import cos, sin

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.utils import x_rotation, z_rotation, y_rotation


def calcALPHA(alpha):
    return x_rotation(alpha)


def calcDELTA(delta):
    return z_rotation(-delta)


def calcGAMMA(gamma):
    return x_rotation(gamma)


def calcOMEGA(omega):
    return z_rotation(-omega)


def calcCHI(chi):
    return y_rotation(chi)


def calcPHI(phi):
    return z_rotation(-phi)


def createVliegMatrices(alpha=None, delta=None, gamma=None, omega=None,
                        chi=None, phi=None):

    ALPHA = None if alpha is None else calcALPHA(alpha)
    DELTA = None if delta is None else calcDELTA(delta)
    GAMMA = None if gamma is None else calcGAMMA(gamma)
    OMEGA = None if omega is None else calcOMEGA(omega)
    CHI = None if chi is None else calcCHI(chi)
    PHI = None if phi is None else calcPHI(phi)
    return ALPHA, DELTA, GAMMA, OMEGA, CHI, PHI


def createVliegsSurfaceTransformationMatrices(sigma, tau):
    """[SIGMA, TAU] = createVliegsSurfaceTransformationMatrices(sigma, tau)
    angles in radians
    """
    SIGMA = matrix([[cos(sigma), 0, sin(sigma)],
                    [0, 1, 0], \
                    [-sin(sigma), 0, cos(sigma)]])

    TAU = matrix([[cos(tau), sin(tau), 0],
                  [-sin(tau), cos(tau), 0],
                  [0, 0, 1]])
    return(SIGMA, TAU)


def createVliegsPsiTransformationMatrix(psi):
    """PSI = createPsiTransformationMatrices(psi)
    angles in radians
    """
    return matrix([[1, 0, 0],
                   [0, cos(psi), sin(psi)],
                   [0, -sin(psi), cos(psi)]])
