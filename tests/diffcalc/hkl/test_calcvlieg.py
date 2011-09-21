from tests.diffcalc import scenarios
import unittest
from mock import Mock
import random
from math import pi
from diffcalc.utils import createVliegMatrices
try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix
from diffcalc.hkl.calcvlieg import VliegHklCalculator,\
    _findOmegaAndChiToRotateHchiIntoQalpha

TORAD=pi/180
TODEG=180/pi

def createMockUbcalc(UB):
    ubcalc = Mock()
    ubcalc.getTau.return_value = 0
    ubcalc.getSigma.return_value = 0
    ubcalc.getUBMatrix.return_value = UB
    return ubcalc


def createMockHardwareMonitor():
    hardware = Mock()
    hardware.getPosition.return_value = (0.0,0.0,0.0)
    hardware.getPhysicalAngleNames.return_value = 'madeup','alpha','gamma'
    return hardware


def createMockDiffractometerGeometry():
    geometry = Mock()
    geometry.getUnchangableParametersDictionary.return_value = {}
    geometry.isParameterFixed.return_value = False
    geometry.supportsModeGroup.return_value = True
    geometry.getFixedParameters.return_value = {}
    geometry.getName.return_value = 'mock'
    geometry.getSupportedModes.return_value =  {}
    geometry.gammaLocation.return_value = 'arm'
    return geometry


###################################################################################

class TestVliegCoreMathBits(unittest.TestCase):
    
    def setUp(self):
        self.many = [-91, -90, -89, -46, -45, -44, -1, 0, 1, 44, 45, 46, 89, 90, 91]
        self.many = self.many + map(lambda x:x+180, self.many) + map(lambda x:x-180, self.many)
    
    def test__findOmegaAndChiToRotateHchiIntoQalpha_WithIntegerValues(self):
        for omega in self.many:
            for chi in self.many:
                self.try__findOmegaAndChiToRotateHchiIntoQalpha(omega, chi)
                #print str(omega), ",", str(chi)
    
    def SKIP_test__findOmegaAndChiToRotateHchiIntoQalpha_WithRandomValues(self):
        for _ in range(10):
            for omega in self.many:
                for chi in self.many:
                    omega = omega + random.uniform(-.001, .001)
                    chi = chi + random.uniform(-.001, .001)
                    self.try__findOmegaAndChiToRotateHchiIntoQalpha(omega, chi)
                    #print str(omega), ",", str(chi)
    
    def test__findOmegaAndChiToRotateHchiIntoQalpha_WithTrickyOnes(self):
        tricky_ones = [(-45.000000 ,-180.000000), (45.000000 ,-180.000000), (135.000000 ,-180.000000), (225.000000, .000000), (225.000000 ,.000000), (225.000000 ,-180.000000), (-225.000000 ,.000000), (-225.000000 ,.000000), (-225.000000 ,-180.000000), (-135.000000 ,-180.000000), (89.998894 ,-44.999218)]
        for omega, chi in tricky_ones:
            self.try__findOmegaAndChiToRotateHchiIntoQalpha(omega, chi)

    def try__findOmegaAndChiToRotateHchiIntoQalpha(self, omega, chi):
        h_chi = Matrix( [ [1], [1], [1]] )
        h_chi= h_chi.times(1/h_chi.norm1())
        [_, _, _, OMEGA, CHI, _] = createVliegMatrices(None, None, None, omega*TORAD, chi*TORAD, None)
        q_alpha = OMEGA.times(CHI).times(h_chi)
        try:
            omega_calc, chi_calc  = _findOmegaAndChiToRotateHchiIntoQalpha(h_chi, q_alpha)
        except ValueError, e:
            raise ValueError(str(e) + "\n, resulting from test where omega:%f chi%f" % (self.omega, self.chi))
        [_, _, _, OMEGA, CHI, _] = createVliegMatrices(None, None, None, omega_calc, chi_calc, None)
        self.assertArraysNearlyEqual(OMEGA.times(CHI).times(h_chi), q_alpha, .000001, "omega: %f chi:%f" % (omega, chi))

    def assertArraysNearlyEqual(self, first, second, tolerance, contextString=''):
        """Fail if the norm of the difference between two arrays is greater than
           the given tolerance.
        """
        diff = first.minus(second)
        if diff.normF() >= tolerance:
            raise self.failureException, ('\n%s !=\n %s\ncontext: %s' % (`first.array`, `second.array`, contextString))



class BaseTestHklCalculator():

    def setSessionAndCalculation(self):
        raise Exception("Abstract")

    def setUp(self):            
        self.ac = VliegHklCalculator(None, createMockDiffractometerGeometry(), createMockHardwareMonitor())    
        self.ac.raiseExceptionsIfAnglesDoNotMapBackToHkl = True
        self.setSessionAndCalculation()

    def testAnglesToHkl(self):
        mockUbcalc = createMockUbcalc(Matrix(self.sess.umatrix).times(Matrix(self.sess.bmatrix)))
                                
        self.ac = VliegHklCalculator(mockUbcalc, createMockDiffractometerGeometry(), createMockHardwareMonitor())
        self.ac.raiseExceptionsIfAnglesDoNotMapBackToHkl = True

        # Check the two given reflections
        (hklactual1, params) = self.ac.anglesToHkl(self.sess.ref1.pos, self.sess.ref1.energy)
        del params
        (hklactual2, params) = self.ac.anglesToHkl(self.sess.ref2.pos, self.sess.ref2.energy)
        self.assert_(Matrix([hklactual1]).minus(Matrix([self.sess.ref1calchkl])).normF()<=.0003, "wrong hkl calcualted from ref1 angles for scenario.names.name="+self.sess.name)
        self.assert_(Matrix([hklactual2]).minus(Matrix([self.sess.ref2calchkl])).normF()<=.0003, "wrong hkl calcualted from ref2 angles for scenario.names.name="+self.sess.name)

        # ... znd in each calculation through the hkl/posiiont pairs
        if self.calc:
            for hkl, pos, param in zip(self.calc.hklList, self.calc.posList, self.calc.paramList):
                (hkl_actual, params) = self.ac.anglesToHkl(pos, self.calc.energy)
                self.assert_(Matrix([hkl_actual]).minus(Matrix([hkl])).normF()<=.0003,\
                            "wrong hkl calcualted for scenario.name=%s, calculation.tag=%s\n  expected hkl=(%f,%f,%f)\ncalculated hkl=(%f,%f,%f)"%(self.sess.name, self.calc.tag, hkl[0],hkl[1],hkl[2],hkl_actual[0],hkl_actual[1],hkl_actual[2]) )
                print "***anglesToHkl***"
                print "*** ", str(hkl), " ***"
                print params
                print param
    
    def testHklToAngles(self):
        if self.calc:
            # Configure the angle calculator for this session scenario
            mockUbcalc = createMockUbcalc(Matrix(self.sess.umatrix).times(Matrix(self.sess.bmatrix)))
            hw = createMockHardwareMonitor()
            ac = VliegHklCalculator(mockUbcalc, createMockDiffractometerGeometry(), hw)
            ac.raiseExceptionsIfAnglesDoNotMapBackToHkl = True

            ## configure the angle calculator for this calculation
            ac.mode_selector.setModeByName(self.calc.modeToTest)
            
            # Set fixed parameters
            if self.calc.modeToTest in ('4cBeq','4cFixedw'):
    
                #ac.setParameter('alpha', self.calc.alpha )
                ac.parameter_manager.setTrackParameter('alpha',True)
                hw.getPosition.return_value = 888, self.calc.alpha, 999
                ac.parameter_manager.setParameter('gamma', self.calc.gamma )
    
            # Test each hkl/position pair
            for idx in range(len(self.calc.hklList)):
                hkl=self.calc.hklList[idx]
                expectedpos = self.calc.posList[idx]
                (pos, params) = ac.hklToAngles(hkl[0], hkl[1], hkl[2], self.calc.energy)
                self.assert_(pos.nearlyEquals(expectedpos, 0.01),\
                            "wrong positions calculated for TestScenario=%s, AngleTestScenario=%s, hkl=(%f,%f,%f):\n  expected pos=%s;\n  returned pos=%s "\
                            %(self.sess.name, self.calc.tag,hkl[0], hkl[1], hkl[2], str(expectedpos), str(pos)) )
                print "*** hklToAngles ***"
                print "*** ", str(hkl), " ***"
                print params
                try:
                    print self.calc.paramList[idx]
                except IndexError: # Not always specified
                    pass




class TestVliegHklCalculatorSess1NoCalc(BaseTestHklCalculator, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session1
        self.calc = None


class TestVliegHklCalculatorSess2Calc0(BaseTestHklCalculator, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session2
        self.calc = scenarios.session2.calculations[0]


class TestVliegHklCalculatorSess3Calc0(BaseTestHklCalculator, unittest.TestCase):
    def setSessionAndCalculation(self):
        self.sess = scenarios.session3
        self.calc = scenarios.session3.calculations[0]