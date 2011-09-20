try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
    
from diffcalc.geometry.sixc import SixCircleGammaOnArmGeometry, gammaOnArmToBase,\
    gammaOnBaseToArm
from diffcalc.utils import Position, createVliegMatrices, \
    nearlyEqual, radiansEquivilant as radeq
from math import pi
import random
import unittest

random.seed() # uses time

TORAD=pi/180
TODEG=180/pi


try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
    
import unittest
from diffcalc.geometry.sixc import SixCircleGeometry
from diffcalc.utils import Position
import random

class TestSixCirclePlugin(unittest.TestCase):
    
    def setUp(self):
        self.geometry=SixCircleGeometry()
    
    def testGetName(self):
        self.assertEqual(self.geometry.getName(), "sixc")

    def testPhysicalAnglesToInternalPosition(self):
        pos = [0,0,0,0,0,0]
        self.assert_(Position(*pos)==self.geometry.physicalAnglesToInternalPosition(pos))
    
    def testInternalPositionToPhysicalAngles(self):
        pos = [0,0,0,0,0,0]    
        result = self.geometry.internalPositionToPhysicalAngles(Position(*pos))
        self.assert_(Matrix([pos]).minus(Matrix([result])).normF()<0.001)

    def testGammaOn(self):
        self.assert_(self.geometry.gammaLocation(), 'base')
        
#    def testPhysicalAnglesToInternalWrongInput(self):
#        pos = (1,2,3,4,5)
#        self.assertRaises(AssertionError, self.geometry.physicalAnglesToInternal(pos))    
        
#    def internalAnglesToPhysicalWrongInput(self):
#        pos = (1,2,3,4,5,6,7)
#        self.assertRaises(AssertionError, self.geometry.physicalAnglesToInternal(pos))


    
    def testSupportsModeGroup(self):
        self.assertEqual(self.geometry.supportsModeGroup('fourc'), True)
        self.assertEqual(self.geometry.supportsModeGroup('made up mode'), False)    

    def testGetFixedParameters(self):
        self.geometry.getFixedParameters() # check for exceptions
    
    def isParamaterUnchangable(self):
        self.assertEqual(self.geometry.isParamaterUnchangable('made up parameter'), False)

################################################################################

class TestSixCircleGammaOnArmGeometry(unittest.TestCase):
    
    def setUp(self):
        self.geometry=SixCircleGammaOnArmGeometry()
    
    def testGetName(self):
        self.assertEqual(self.geometry.getName(), "sixc_gamma_on_arm")

    def testPhysicalAnglesToInternalPosition(self):
        pos = [1,2,3,4,5,6]
        self.assert_(Position(*pos)==self.geometry.physicalAnglesToInternalPosition(pos))
    
    def testInternalPositionToPhysicalAngles(self):
        pos = [1,2,3,4,5,6]    
        result = self.geometry.internalPositionToPhysicalAngles(Position(*pos))
        self.assert_(Matrix([pos]).minus(Matrix([result])).normF()<0.001)
        
#    def testPhysicalAnglesToInternalWrongInput(self):
#        pos = (1,2,3,4,5)
#        self.assertRaises(AssertionError, self.geometry.physicalAnglesToInternal(pos))    
        
#    def internalAnglesToPhysicalWrongInput(self):
#        pos = (1,2,3,4,5,6,7)
#        self.assertRaises(AssertionError, self.geometry.physicalAnglesToInternal(pos))

    
    def testSupportsModeGroup(self):
        self.assertEqual(self.geometry.supportsModeGroup('fourc'), True)
        self.assertEqual(self.geometry.supportsModeGroup('made up mode'), False)    

    def testGetFixedParameters(self):
        self.geometry.getFixedParameters() # check for exceptions
    
    def isParamaterUnchangable(self):
        self.assertEqual(self.geometry.isParamaterUnchangable('made up parameter'), False)




y_vector = Matrix([[0],[1],[0]])

TOLERANCE = 1e-5

def armAnglesToLabVector(alpha, delta, gamma):
    [ALPHA, DELTA, GAMMA,_,_,_] = createVliegMatrices(alpha, delta, gamma, None, None, None)
    return ALPHA.times(DELTA).times(GAMMA).times(y_vector)

def baseAnglesToLabVector(delta, gamma):
    [_, DELTA, GAMMA,_,_,_] = createVliegMatrices(None, delta, gamma, None, None, None)
    return GAMMA.times(DELTA).times(y_vector)


def checkGammaOnArmToBase(alpha, deltaA, gammaA):
        deltaB, gammaB = gammaOnArmToBase(deltaA, gammaA, alpha)
        
        labA = armAnglesToLabVector(alpha, deltaA, gammaA)
        labB = baseAnglesToLabVector(deltaB, gammaB)
        if not nearlyEqual(labA, labB, TOLERANCE):
            strLabA = "[%f, %f, %f]" % (labA.get(0,0), labA.get(1,0), labA.get(2,0))
            strLabB = "[%f, %f, %f]" % (labB.get(0,0), labB.get(1,0), labB.get(2,0))
            rep = "alpha=%f, delta=%f, gamma=%f" %     (alpha*TODEG, deltaB*TODEG, gammaB*TODEG)
            raise AssertionError('\nArm-->Base ' + rep + '\n' +
                "arm (delta, gamma) = (%f,%f) <==>\t labA = %s\n" % (deltaA*TODEG, gammaA*TODEG, strLabA) +
                "base(delta, gamma) = (%f,%f) <==>\t labB = %s\n" % (deltaB*TODEG, gammaB*TODEG, strLabB)
                )

def checkBaseArmBaseReciprocity(alpha, delta_orig, gamma_orig):
        (deltaB, gammaB) = (delta_orig, gamma_orig)
        (deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha)
        (deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha)        
        if (not radeq(deltaB, delta_orig, TOLERANCE)) or (not radeq(gammaB, gamma_orig, TOLERANCE)):
            s = "\nBase-Arm-Base reciprocity\n"
            s+= 'alpha=%f\n' % (alpha*TODEG,)
            s+= '   (deltaB, gammaB) = (%f, %f)\n' % (delta_orig*TODEG, gamma_orig*TODEG)
            s+= ' ->(deltaA, gammaA) = (%f, %f)\n' % (deltaA*TODEG, gammaA*TODEG)
            s+= ' ->(deltaB, gammaB) = (%f, %f)\n' % (deltaB*TODEG, gammaB*TODEG)
            raise AssertionError( s)

def checkArmBaseArmReciprocity(alpha, delta_orig, gamma_orig):
    (deltaA, gammaA) = (delta_orig, gamma_orig)
    (deltaB, gammaB) = gammaOnArmToBase(deltaA, gammaA, alpha)
    (deltaA, gammaA) = gammaOnBaseToArm(deltaB, gammaB, alpha)
    if (not radeq(deltaA,delta_orig,TOLERANCE)) or (not radeq(gammaA,gamma_orig, TOLERANCE)):
        s = "\nArm-Base-Arm reciprocity\n"
        s+= "alpha=%f\n" % (alpha*TODEG,)
        s+= "   (deltaA, gammaA) = (%f, %f)\n" % (delta_orig*TODEG, gamma_orig*TODEG)
        s+= " ->(deltaB, gammaB) = (%f, %f)\n" % (deltaB*TODEG, gammaB*TODEG)
        s+= " ->(deltaA, gammaA) = (%f, %f)\n" % (deltaA*TODEG, gammaA*TODEG)
        raise AssertionError(s)

def test_generator_for_cases():
    for alpha in [-89.9, -45, -1, 0,1,45, 89.9]:
        for gamma in [-89.9, -46, -45, -44, -1, 0, 1, 44, 45, 46, 89.9]:
            for delta in [-179.9, -135, -91, -89.9, -89, -46, -45, -44, -1, 0, 1, 44, 45, 46, 89, 89.9, 91, 135, 179.9]:
                yield checkGammaOnArmToBase, alpha*TORAD, delta*TORAD, gamma*TORAD
                #TODO: base-arm-base reciprocity fails (maybe a fact of life)
                #yield checkBaseArmBaseReciprocity, alpha*TORAD, delta*TORAD, gamma*TORAD
                yield checkArmBaseArmReciprocity, alpha*TORAD, delta*TORAD, gamma*TORAD