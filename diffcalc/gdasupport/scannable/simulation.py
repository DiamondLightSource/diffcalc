from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.hkl.vlieg.calcvlieg import vliegAnglesToHkl
from diffcalc.hkl.vlieg.matrices import createVliegMatrices
try:
    from gda.device.scannable import PseudoDevice
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.scannable import Scannable as PseudoDevice
import time
from math import sqrt, pi, exp

TORAD = pi / 180
TODEG = 180 / pi

class Equation(object):
    
    def __call__(self, dh, dk, dl):
        raise Exception('Abstract')
    
    def __str__(self):
        "Abstract equation"
    
class Gaussian(Equation):
    
    def __init__(self, variance):
        self.variance = float(variance)
        
    def __call__(self, dh, dk, dl):
        dr_squared = dh * dh + dk * dk + dl * dl
        return 1 / sqrt(2 * pi * self.variance) * exp(-dr_squared / (2 * self.variance))
        

class SimulatedCrystalCounter(PseudoDevice):

    def __init__(self , name, diffractometerScannable, geometryPlugin, wavelengthScannable, equation=Gaussian(.01)):
        self.setName(name)
        self.setInputNames([name + '_count'])
        #elf.setExtraNames([name+'_count'])
        self.setOutputFormat(['%7.5f'])#*2)
        self.exposureTime = 1
        self.pause = True
        self.diffractometerScannable = diffractometerScannable
        self.geometry = geometryPlugin
        self.wavelengthScannable = wavelengthScannable
        self.equation = equation
        
        self.cut = None
        self.UB = None
        self.chiMissmount = 0.
        self.phiMissmount = 0.
        self.setCrystal('cubic', 1, 1, 1, 90, 90, 90)
        
    def setCrystal(self, name, a, b, c, alpha, beta, gamma):
        self.cut = CrystalUnderTest(name, a, b, c, alpha, beta, gamma)
        self.calcUB()

    def setChiMissmount(self, chi):
        self.chiMissmount = chi
        self.calcUB()
        
    def setPhiMissmount(self, phi):
        self.phiMissmount = phi
        self.calcUB()
        
    def calcUB(self):
        [_, _, _, _, CHI, PHI] = createVliegMatrices(None, None, None, None, self.chiMissmount * TORAD, self.phiMissmount * TORAD)
        self.UB = CHI * PHI  * self.cut.getBMatrix( )

    def asynchronousMoveTo(self, exposureTime):
        self.exposureTime = exposureTime
        if self.pause:
            time.sleep(exposureTime)
    
    def getPosition(self):
        h, k, l = self.getHkl()
        dh, dk, dl = h - round(h), k - round(k), l - round(l)
        count = self.equation(dh, dk, dl)
        #return self.exposureTime, count*self.exposureTime
        return count * self.exposureTime

    def getHkl(self):
        pos = self.geometry.physicalAnglesToInternalPosition(self.diffractometerScannable.getPosition())
        pos.changeToRadians()
        wavelength = self.wavelengthScannable.getPosition()
        return vliegAnglesToHkl(pos, wavelength, self.UB)

    def isBusy(self):
        return False
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        s = 'simulated crystal detector: %s\n' % self.getName()
        h, k, l = self.getHkl()
        s += '   h : %f\n' % h
        s += '   k : %f\n' % k
        s += '   l : %f\n' % l
        s += self.cut.__str__()
        s += "chi orientation: %s\n" % self.chiMissmount
        s += "phi orientation: %s\n" % self.phiMissmount
        ub = self.UB.tolist()
        s += "UB:\n"
        s += "       % 18.13f% 18.13f% 18.12f\n" % (ub[0][0], ub[0][1], ub[0][2])
        s += "     % 18.13f% 18.13f% 18.12f\n" % (ub[1][0], ub[1][1], ub[1][2])
        s += "     % 18.13f% 18.13f% 18.12f\n" % (ub[2][0], ub[2][1], ub[2][2])
        return s
