from diffcalc.utils import AbstractPosition
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

from math import pi

TORAD = pi / 180
TODEG = 180 / pi

class YouPosition(AbstractPosition):

    def __init__(self, mu=None, delta=None, nu=None, eta=None, chi=None, phi=None):
        self.mu = mu
        self.delta = delta
        self.nu = nu
        self.eta = eta
        self.chi = chi
        self.phi = phi
    
    def clone(self):
        return YouPosition(self.mu, self.delta, self.nu, self.eta, self.chi, self.phi)
        
    def changeToRadians(self):
        self.mu *= TORAD
        self.delta *= TORAD
        self.nu *= TORAD
        self.eta *= TORAD
        self.chi *= TORAD
        self.phi *= TORAD

    def changeToDegrees(self):
        self.mu *= TODEG
        self.delta *= TODEG
        self.nu *= TODEG
        self.eta *= TODEG
        self.chi *= TODEG
        self.phi *= TODEG

    def totuple(self):
        return (self.mu, self.delta, self.nu, self.eta, self.chi, self.phi)
    
    def __str__(self):
        return "YouPosition(mu %s delta: %s nu: %s eta: %s chi: %s  phi: %s)" % \
              (`self.mu`, `self.delta`, `self.nu`, `self.eta`, `self.chi`, `self.phi`)
                  
   